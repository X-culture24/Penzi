import psycopg2
import random

# Database connection
conn = psycopg2.connect(
    dbname="penzi_app",
    user="kevin",
    password="kevin123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Helper function to insert users
def insert_user(name, age, gender, county, town, phone_number, education, profession, marital_status, religion, ethnicity, description):
    try:
        # Check for duplicate phone number
        cursor.execute("SELECT id FROM \"user\" WHERE phone_number = %s;", (phone_number,))
        if cursor.fetchone():
            print(f"⚠️ Skipping user (phone number exists): {name}")
            return

        # Insert user
        cursor.execute("""
            INSERT INTO "user" (name, age, gender, county, town, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (name, age, gender, county, town, phone_number))

        user_id = cursor.fetchone()[0]

        # Insert user details
        cursor.execute("""
            INSERT INTO "user_details" (user_id, level_of_education, profession, marital_status, religion, ethnicity)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user_id, education, profession, marital_status, religion, ethnicity))

        # Insert self-description
        cursor.execute("""
            INSERT INTO "self_description" (user_id, description)
            VALUES (%s, %s);
        """, (user_id, description))

        print(f"✅ Inserted user: {name}")

    except Exception as e:
        print(f"❌ Error inserting user: {name} - {e}")

# Data for generating users
male_names = [
    ("Brian Odhiambo", "Luo"), ("John Kamau", "Kikuyu"), ("Kevin Wafula", "Luhya"),
    ("Peter Kiptoo", "Kalenjin"), ("James Mwenda", "Meru"), ("Sammy Wambua", "Kamba"),
    ("David Kipchumba", "Kalenjin"), ("Anthony Omondi", "Luo"), ("Michael Njoroge", "Kikuyu"),
    ("Collins Simiyu", "Luhya"), ("Victor Mutua", "Kamba"), ("Kelvin Wekesa", "Luhya"),
    ("Isaac Chepkoech", "Kalenjin"), ("George Karani", "Kikuyu"), ("Felix Otieno", "Luo")
]

female_names = [
    ("Lydia Atieno", "Luo"), ("Grace Wanjiru", "Kikuyu"), ("Joyce Nekesa", "Luhya"),
    ("Cynthia Chebet", "Kalenjin"), ("Diana Mwikali", "Kamba"), ("Ruth Muthoni", "Kikuyu"),
    ("Esther Nyambura", "Kikuyu"), ("Lucy Akinyi", "Luo"), ("Faith Chepkorir", "Kalenjin"),
    ("Naomi Naliaka", "Luhya"), ("Beatrice Makau", "Kamba"), ("Violet Jepchirchir", "Kalenjin"),
    ("Eunice Wambui", "Kikuyu"), ("Angela Moraa", "Kisii"), ("Janet Kivuva", "Kamba")
]

counties_and_towns = [
    ("Nairobi County", "Nairobi"), ("Mombasa County", "Mombasa"), ("Kisumu County", "Kisumu")
]

education_levels = ["Graduate", "Undergraduate", "Diploma"]
professions = ["Engineer", "Doctor", "Teacher", "Lawyer", "Entrepreneur", "Nurse"]
marital_statuses = ["Single", "Divorced"]
religions = ["Christianity", "Islam"]
descriptions = [
    "Outgoing and adventurous.", "Passionate about technology.", "Love meeting new people.",
    "Dedicated to helping others.", "Curious and open-minded.", "Enjoys deep conversations."
]

def generate_users():
    for name, ethnicity in male_names + female_names:
        age = random.randint(18, 44)
        gender = "Male" if (name, ethnicity) in male_names else "Female"
        county, town = random.choice(counties_and_towns)
        phone_number = f"07{random.randint(10000000, 99999999)}"
        education = random.choice(education_levels)
        profession = random.choice(professions)
        marital_status = random.choice(marital_statuses)
        religion = random.choice(religions)
        description = random.choice(descriptions)

        insert_user(name, age, gender, county, town, phone_number, education, profession, marital_status, religion, ethnicity, description)

# Generate and insert 30 users
generate_users()

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("✅ All users inserted successfully!")
