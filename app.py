import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message
from dotenv import load_dotenv

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Secret Key (for session handling)
app.secret_key = os.urandom(24)

# ✅ Enable CORS
CORS(app)

# ✅ Database Configuration (from .env)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
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
            return "You are already registered. To search for a MPENZI, SMS match#age#town. E.g., match#23-25#Kisumu"
        return "Welcome to our dating service with 6000 potential dating partners! To register SMS start#name#age#gender#county#town. E.g., start#John Doe#26#Male#Nakuru#Naivasha"

    # 🟢 Handle User Registration - Check if already registered
    elif user_input.startswith("start#"):
        if user:
            return "You are already registered. To search for a MPENZI, SMS match#age#town. E.g., match#23-25#Kisumu"
            
        try:
            _, name, age, gender, county, town = user_input.split("#")
            age = int(age)
        except (ValueError, TypeError):
            return "Invalid format. Use: start#name#age#gender#county#town."

        user = create_new_user(phone_number, name, age, gender, county, town)
        return f"Your profile has been created successfully {name}. SMS details#levelOfEducation#profession#martialStatus#religion#ethnicity. E.g. details#diploma#driver#single#christian#mijikenda"

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

        return "This is the last stage of registration. SMS a brief description of yourself starting with the word MYSELF. E.g., MYSELF chocolate, lovely, sexy etc."

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

        return "You are now registered for dating. To search for a MPENZI, SMS match#age#town E.g., match#23-25#Kisumu"

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
        return f"We have {len(matches)} who match your choice! We will send you details of {len(matches)} of them shortly. To get more details about a person, Send DETAILS 0712345678\n{match_info}"

    # 🟢 Handle Phone Number Lookup
    elif user_input.isdigit() and len(user_input) == 10:
        if not user:
            return "Please register first using: start#name#age#gender#county#town."

        target_user = get_user_by_phone(user_input)
        if not target_user:
            return "User not found."

        user_details = UserDetails.query.filter_by(user_id=target_user.id).first()
        if not user_details:
            return f"No details available for {target_user.name}."

        # Notify the Requested User
        notify_user(user_input, f"Hi {target_user.name}, someone is interested in you. Send YES to confirm.")

        return (
            f"{target_user.name} ({target_user.age} years) from {target_user.town}.\n"
            f"Education: {user_details.level_of_education}, Profession: {user_details.profession}, "
            f"Marital: {user_details.marital_status}, Religion: {user_details.religion}, Ethnicity: {user_details.ethnicity}.\n"
            f"Send DESCRIBE {target_user.phone_number} to know more about them."
        )

    # 🟢 Handle User Confirmation (YES Command)
    elif user_input == "yes":
        # Check if there is a pending match
        pending_match = Match.query.filter_by(phone_number=phone_number, status="pending").first()
        if pending_match:
            # Update to 'approved' if both users confirm
            pending_match.status = "approved"
            db.session.commit()

            # Notify both users on mutual approval
            notify_user(phone_number, "Mutual interest confirmed! You can now message each other.")
            notify_user(pending_match.target_phone, "Mutual interest confirmed! You can now message each other.")
            return "Match confirmed! You can now message each other."

        # Otherwise, initiate a new match request
        return "Confirmation sent. Awaiting confirmation from the other user."

    # 🟢 DESCRIBE <phone_number>
    elif user_input.startswith("DESCRIBE"):
        if not user:
            return "Please register first using: start#name#age#gender#county#town."

        try:
            _, target_phone = user_input.split(" ")
        except ValueError:
            return "Invalid format. Use: DESCRIBE <phone_number>"

        target_user = get_user_by_phone(target_phone)
        if not target_user:
            return "User not found."

        description = SelfDescription.query.filter_by(user_id=target_user.id).first()
        if not description:
            return f"No self-description available for {target_user.name}."

        return f"{target_user.name} describes themselves as: {description.description}."

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


# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)