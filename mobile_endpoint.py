import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Secret Key (for session handling)
app.secret_key = os.urandom(24)

# ✅ Enable CORS
CORS(app)

# ✅ Database Configuration (PostgreSQL)
DATABASE_URI = "postgresql://kevin:kevin123@localhost:5432/penzi_app"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize DB and Migrations
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Helper: Save Message
def save_message(from_user_id, to_user_id, message_content):
    new_message = Message(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        message_content=message_content
    )
    db.session.add(new_message)
    db.session.commit()
    return new_message

# ✅ Helper: Get User by Phone Number
def get_user_by_phone(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()

# ✅ Helper: Notify User (Simulate Notification)
def notify_user(target_phone, content):
    print(f"📢 Notification to {target_phone}: {content}")

# ✅ Helper: Create New User
def create_new_user(phone_number, name, age, gender, county, town):
    new_user = User(
        phone_number=phone_number,
        name=name,
        age=age,
        gender=gender.capitalize(),
        county=county,
        town=town
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

# ✅ Main Chatbot Endpoint
@app.route("/penzi", methods=["POST"])
def penzi_chatbot():
    data = request.json
    phone_number = data.get("phone_number")
    user_input = data.get("message")

    if not phone_number or not user_input:
        return jsonify({"error": "phone_number and message are required"}), 400

    # 🟢 Fetch the User
    user = get_user_by_phone(phone_number)

    # Save User Message (User Input)
    if user:
        save_message(user.id, None, user_input)

    # Process Input and Get Response
    response = process_user_input(user, user_input, phone_number)

    # Save System Response (System Output)
    if user:
        save_message(None, user.id, response)

    return jsonify({"response": response})

# ✅ Process User Input (UPDATED TO FILTER REGISTERED USERS)
def process_user_input(user, user_input, phone_number):
    user_input = user_input.strip()

    # 🟢 Activation Command - Check if user exists
    if user_input.lower() == "penzi":
        if user:
            return "You are already registered. To search for a MPENZI, SMS match#age#town to 22141. E.g., match#23-25#Kisumu"
        return "Welcome to our dating service with 6000 potential dating partners! To register SMS start#name#age#gender#county#town to 22141. E.g., start#John Doe#26#Male#Nakuru#Naivasha"

    # 🟢 Handle User Registration - Check if already registered
    elif user_input.startswith("start#"):
        if user:
            return "You are already registered. To search for a MPENZI, SMS match#age#town to 22141. E.g., match#23-25#Kisumu"
            
        try:
            _, name, age, gender, county, town = user_input.split("#")
            age = int(age)
        except (ValueError, TypeError):
            return "Invalid format. Use: start#name#age#gender#county#town."

        user = create_new_user(phone_number, name, age, gender, county, town)
        return f"Your profile has been created successfully {name}. SMS details#levelOfEducation#profession#martialStatus#religion#ethnicity to 22141. E.g. details#diploma#driver#single#christian#mijikenda"

    # 🟢 Handle Details Registration
    elif user_input.startswith("details#"):
        if not user:
            return "Please register first using: start#name#age#gender#county#town."

        try:
            _, education, profession, marital_status, religion, ethnicity = user_input.split("#")
        except ValueError:
            return "Invalid format. Use: details#education#profession#maritalStatus#religion#ethnicity"

        details = UserDetails(
            user_id=user.id,
            level_of_education=education,
            profession=profession,
            marital_status=marital_status,
            religion=religion,
            ethnicity=ethnicity
        )
        db.session.add(details)
        db.session.commit()

        return "This is the last stage of registration. SMS a brief description of yourself to 22141 starting with the word MYSELF. E.g., MYSELF chocolate, lovely, sexy etc."

    # 🟢 Handle Self Description
    elif user_input.startswith("MYSELF"):
        if not user:
            return "Please register first using: start#name#age#gender#county#town."

        description = user_input[6:].strip()
        self_desc = SelfDescription(
            user_id=user.id,
            description=description
        )
        db.session.add(self_desc)
        db.session.commit()

        return "You are now registered for dating. To search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams. E.g., match#23-25#Kisumu"

    # 🟢 Handle Match Request
    elif user_input.startswith("match#"):
        if not user:
            return "Please register first using: start#name#age#gender#county#town."

        try:
            _, age_range, town = user_input.split("#")
        except ValueError:
            return "Invalid format. Use: match#ageRange#town (e.g., match#25-35#Nairobi)."

        session.setdefault("match_offset", 0)
        matches = get_matches(user, age_range, town, session["match_offset"])

        if not matches:
            session.pop("match_offset", None)
            return "No more matches available. Try a different age range or town."

        session["match_offset"] += 3
        match_info = "\n".join(
            f"{m.name} aged {m.age}, {m.phone_number}."
            for m in matches
        )
        return f"We have {len(matches)} who match your choice! We will send you details of {len(matches)} of them shortly. To get more details about a person, SMS their number e.g., 0722010203 to 22141\n{match_info}"

    # 🟢 Default Invalid Command
    else:
        return "Invalid command. Try again."

# ✅ Fetch Matches in Batches of 3 (Opposite Gender)
def get_matches(user, age_range, town, offset):
    try:
        min_age, max_age = map(int, age_range.split("-"))
    except ValueError:
        return []

    opposite_gender = "Male" if user.gender == "Female" else "Female"

    matches = User.query.filter(
        User.gender == opposite_gender,
        User.age >= min_age,
        User.age <= max_age,
        User.town.ilike(f"%{town}%"),
        User.id != user.id
    ).offset(offset).limit(3).all()

    return matches

# ✅ Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"response": "server is up and running"})

if __name__ == "__main__":
    # Allow external devices to connect (e.g., Android emulator)
    app.run(host="0.0.0.0", port=5000, debug=True)