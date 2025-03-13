import psycopg2
import bcrypt

# Database connection
conn = psycopg2.connect(
    dbname="penzi_app",
    user="kevin",
    password="kevin123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Helper function to insert a user and related details
def insert_user(name, age, gender, county, town, phone_number, password, education, profession, marital_status, religion, ethnicity, description):
    try:
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert user
        cursor.execute("""
            INSERT INTO "user" (name, age, gender, county, town, phone_number, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (name, age, gender, county, town, phone_number, hashed_password))

        user_id = cursor.fetchone()[0]

        # Insert user details
        cursor.execute("""
            INSERT INTO "user_details" (user_id, level_of_education, profession, marital_status, religion, ethnicity)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user_id, education, profession, marital_status, religion, ethnicity))

        # Insert self description
        cursor.execute("""
            INSERT INTO "self_description" (user_id, description)
            VALUES (%s, %s);
        """, (user_id, description))

        print(f"✅ Inserted user: {name}")
    except Exception as e:
        print(f"❌ Error inserting user: {name} - {e}")

# Main user (ensure phone number is unique)
insert_user(
    "Test User", 30, "Female", "Nairobi County", "Nairobi", "0712345679", "Password123",
    "Graduate", "Accountant", "Single", "Christianity", "Kikuyu",
    "I am an outgoing person who loves adventure and meaningful conversations."
)

# 9 Matching Users (with unique phone numbers and all arguments)
matching_users = [
    ("Lina Moraa", 29, "Male", "Nairobi County", "Nairobi", "0701002004", "Password123", "Graduate", "Engineer", "Single", "Christianity", "Kisii", "Passionate about technology and innovation."),
    ("Dorine Gakii", 26, "Male", "Nairobi County", "Nairobi", "0701223345", "Password123", "Diploma", "Nurse", "Single", "Christianity", "Meru", "Caring and attentive nurse."),
    ("Aisha Bahati", 27, "Male", "Nairobi County", "Nairobi", "0700112234", "Password123", "Undergraduate", "Doctor", "Single", "Islam", "Swahili", "Dedicated medical professional."),
    ("Pamela Nafula", 26, "Male", "Nairobi County", "Nairobi", "0722040507", "Password123", "Graduate", "Teacher", "Single", "Christianity", "Luhya", "Passionate about empowering young minds."),
    ("Maria Mwende", 28, "Male", "Nairobi County", "Nairobi", "0702556678", "Password123", "Graduate", "Nurse", "Single", "Christianity", "Kamba", "Diligent and dedicated to patient care."),
    ("Keziah Cheptab", 28, "Male", "Nairobi County", "Nairobi", "0708990012", "Password123", "Postgraduate", "Pharmacist", "Single", "Christianity", "Kalenjin", "Lover of books and science."),
    ("Faith Wanjiru", 31, "Male", "Nairobi County", "Nairobi", "0703004006", "Password123", "Undergraduate", "Lawyer", "Single", "Christianity", "Kikuyu", "Advocate for fairness and justice."),
    ("Esther Nduta", 29, "Male", "Nairobi County", "Nairobi", "0711883345", "Password123", "Diploma", "Journalist", "Single", "Christianity", "Kikuyu", "Curious storyteller."),
    ("Joyce Akinyi", 28, "Male", "Nairobi County", "Nairobi", "0714556678", "Password123", "Graduate", "Entrepreneur", "Single", "Christianity", "Luo", "Passionate about business innovation.")
]

for user in matching_users:
    insert_user(*user)

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("✅ All users inserted successfully!")
