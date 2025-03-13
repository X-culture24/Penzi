import random
from faker import Faker
from sqlalchemy import text
from models import db, User, UserDetails, SelfDescription
from app import app
from flask_bcrypt import Bcrypt

# Initialize Faker and Bcrypt
fake = Faker()
bcrypt = Bcrypt()

# ✅ Kenyan Tribes and Ethnic Names (By Tribe)
kenyan_names = {
    "Kikuyu": ["Kamau", "Wanjiku", "Njenga", "Kariuki", "Mwangi"],
    "Luo": ["Odhiambo", "Achieng", "Okoth", "Otieno", "Omondi"],
    "Luhya": ["Wafula", "Naliaka", "Barasa", "Shitandi", "Masinde"],
    "Kalenjin": ["Kipchoge", "Kimutai", "Chebet", "Kiptoo", "Jepkemoi"],
    "Kamba": ["Mutua", "Mutiso", "Ndinda", "Kioko", "Syombua"],
    "Meru": ["Muthomi", "Kaimenyi", "Nkatha", "Mwenda", "Muriithi"],
    "Embu": ["Muchiri", "Ndwiga", "Kithaka", "Njiru", "Kariuki"],
    "Maasai": ["Naisula", "Ole", "Ntimama", "Saitoti", "Sankale"],
    "Taita": ["Mghanga", "Mwabili", "Mwakyoma", "Nyambu", "Mwachofi"],
    "Turkana": ["Ekal", "Lokeris", "Ekidor", "Nakiru", "Alem"],
    "Somali": ["Abdi", "Hassan", "Ahmed", "Ali", "Mohamed"],
    "Mijikenda": ["Chengo", "Masha", "Kazungu", "Kombo", "Mwarandu"],
    "Kisii": ["Mose", "Mokua", "Nyaboke", "Araka", "Osebe"],
    "Kurya": ["Chacha", "Marwa", "Mwita", "Nyang’wara", "Ngicho"],
    "Teso": ["Emong", "Ikwapang", "Ebwom", "Omoding", "Emongole"],
}

# ✅ Kenyan Towns by County (Sampled)
kenyan_towns = {
    "Nairobi": ["Westlands", "Kasarani", "Embakasi", "Lang'ata"],
    "Mombasa": ["Nyali", "Likoni", "Changamwe"],
    "Kisumu": ["Milimani", "Manyatta", "Nyalenda"],
    "Nakuru": ["Naivasha", "Gilgil", "Molo"],
    "Uasin Gishu": ["Eldoret", "Turbo", "Ziwa"],
    "Kiambu": ["Thika", "Ruiru", "Githunguri"],
    "Machakos": ["Athi River", "Mlolongo", "Kangundo"],
    "Meru": ["Maua", "Nkubu", "Timau"],
    "Kakamega": ["Shinyalu", "Lurambi", "Malava"],
    "Kilifi": ["Malindi", "Kilifi Town", "Mariakani"],
}

# ✅ Realistic Kenyan First Names by Gender
male_first_names = [
    "Kevin", "Brian", "John", "Daniel", "Michael", "Joseph", "David", "Isaac", "Peter", "Samuel", "Paul", "Stephen",
    "George", "Dennis", "Vincent", "Simon", "Collins", "Alex", "Patrick", "Mark"
]
female_first_names = [
    "Mary", "Grace", "Faith", "Mercy", "Esther", "Diana", "Alice", "Joy", "Janet", "Ann", "Caroline", "Lucy",
    "Susan", "Elizabeth", "Rose", "Monica", "Agnes", "Catherine", "Beatrice", "Sarah"
]

# ✅ Choices for Other Fields
education_levels = ["Diploma", "Undergraduate", "Postgraduate"]
professions = ["Teacher", "Engineer", "Doctor", "Farmer", "Businessperson", "Software Developer"]
marital_statuses = ["Single", "Married", "Divorced", "Widowed"]
religions = ["Christianity", "Islam", "Hindu"]
password_hash = bcrypt.generate_password_hash("Password123").decode('utf-8')

# ✅ Delete Existing Users
def delete_existing_users():
    with app.app_context():
        try:
            db.session.execute(text('DELETE FROM "user_details"'))
            db.session.execute(text('DELETE FROM "self_description"'))
            db.session.execute(text('DELETE FROM "user"'))
            db.session.commit()
            print("✅ Existing users and related data deleted!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting existing users: {e}")

# ✅ Generate Realistic Descriptions
def generate_realistic_description(gender):
    interests = ["hiking", "traveling", "reading books", "watching movies", "cooking", "sports"]
    traits = ["kind-hearted", "adventurous", "ambitious", "fun-loving", "family-oriented"]
    if gender == "Male":
        return f"I'm a {random.choice(traits)} man who enjoys {random.choice(interests)} and values honesty."
    else:
        return f"I'm a {random.choice(traits)} woman who loves {random.choice(interests)} and meaningful conversations."

# ✅ Generate Test Users
def create_test_users():
    with app.app_context():
        try:
            for _ in range(64):
                gender = random.choice(["Male", "Female"])

                # Select gender-appropriate English name
                if gender == "Male":
                    english_name = random.choice(male_first_names)
                else:
                    english_name = random.choice(female_first_names)

                # Randomly pick a tribe and ethnic name
                tribe = random.choice(list(kenyan_names.keys()))
                ethnic_name = random.choice(kenyan_names[tribe])

                # Combine English and Ethnic Names
                full_name = f"{english_name} {ethnic_name}"

                # Select a random county and town
                county, towns = random.choice(list(kenyan_towns.items()))
                town = random.choice(towns)

                # Create a user
                user = User(
                    name=full_name,
                    age=random.randint(18, 44),
                    gender=gender,
                    county=county,
                    town=town,
                    phone_number=f"07{random.randint(10000000, 99999999)}",
                    password=password_hash,
                )
                db.session.add(user)
                db.session.flush()  # Ensure user ID is available

                # Create user details
                user_details = UserDetails(
                    user_id=user.id,
                    level_of_education=random.choice(education_levels),
                    profession=random.choice(professions),
                    marital_status=random.choice(marital_statuses),
                    religion=random.choice(religions),
                    ethnicity=tribe
                )
                db.session.add(user_details)

                # Create self-description
                self_description = SelfDescription(
                    user_id=user.id,
                    description=generate_realistic_description(gender)
                )
                db.session.add(self_description)

            db.session.commit()
            print("🚀 64 test users generated successfully with gender-appropriate names!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error generating test users: {e}")

if __name__ == "__main__":
    delete_existing_users()
    create_test_users()
