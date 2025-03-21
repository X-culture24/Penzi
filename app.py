import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message
from dotenv import load_dotenv
app = Flask(__name__)
 #✅ Load environment variables from .env file
load_dotenv()

# ✅ Secret Key (for session handling)
app.secret_key = os.urandom(24)

# ✅ Enable CORS
CORS(app)


# ✅ Dynamically load the DATABASE_URL based on the environment
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ✅ Initialize DB and Migrations
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Helper: Save Message
def save_message(phone_number, content, is_system_message=False):
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return None

    new_message = Message(
        from_user_id=user.id,
        to_user_id=None,
        message_content=content,
    )
    db.session.add(new_message)
    db.session.commit()
    return new_message

# ✅ Helper: Get User by Phone Number
def get_user_by_phone(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()

# ✅ Helper: Notify User
def notify_user(target_phone, content):
    save_message(target_phone, content, is_system_message=True)

# ✅ Helper: Fetch Matches in Batches of 3 (Opposite Gender)
def get_matches(user, age_range, town, offset):
    min_age, max_age = map(int, age_range.split("-"))
    opposite_gender = "Male" if user.gender == "Female" else "Female"

    matches = User.query.filter(
        User.gender == opposite_gender,
        User.age >= min_age,
        User.age <= max_age,
        User.town.ilike(town),
        User.id != user.id
    ).offset(offset).limit(3).all()

    return matches

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"response": "server is up"})

# ✅ Main Endpoint
@app.route("/penzi", methods=["POST"])
def penzi_chatbot():
    data = request.json
    phone_number = data.get("phone_number")
    user_input = data.get("message")

    if not phone_number or not user_input:
        return jsonify({"error": "phone_number and message are required"}), 400

    user = get_user_by_phone(phone_number)

    # Save User Message
    save_message(phone_number, user_input, is_system_message=False)

    # Process Input
    response = process_user_input(user, user_input, phone_number)

    # Save System Response
    save_message(phone_number, response, is_system_message=True)

    return jsonify({"response": response, "reply": response})

# ✅ Process User Input
def process_user_input(user, user_input, phone_number):
    user_input = user_input.lower().strip()

    # 🟢 Activation Command
    if user_input == "penzi":
        if user:
            return (
                "Proceed with match requests. You are already registered.\n"
                "Send: match#ageRange#town to find matches.\n"
                "Example: match#25-35#Nairobi"
            )
        return "Welcome to Penzi! To register, send: start#name#age#gender#county#town."

    # 🟢 Handle Match Request
    elif user_input.startswith("match#"):
        try:
            _, age_range, town = user_input.split("#")
        except ValueError:
            return "Invalid format. Use: match#ageRange#town (e.g., match#25-35#Nairobi)."

        # Initialize session offset
        if "match_offset" not in session:
            session["match_offset"] = 0

        # Get matches in batches of 3
        matches = get_matches(user, age_range, town, session["match_offset"])

        if not matches:
            session.pop("match_offset", None)
            return "No more matches available. Try a different age range or town."

        session["match_offset"] += 3

        match_info = "\n".join(
            f"{m.name}, {m.age} years old from {m.town}. Send MOREDETAILS {m.phone_number} to know more."
            for m in matches
        )
        return f"Here are your matches:\n{match_info}"

    # 🟢 MOREDETAILS <phone_number>
    elif user_input.startswith("moredetails"):
        try:
            _, target_phone = user_input.split(" ")
        except ValueError:
            return "Invalid format. Use: MOREDETAILS <phone_number>"

        target_user = get_user_by_phone(target_phone)
        if not target_user:
            return "User not found."

        user_details = UserDetails.query.filter_by(user_id=target_user.id).first()
        if not user_details:
            return f"No details available for {target_user.name}."

        # Notify the Requested User
        notify_user(target_phone, f"Hi {target_user.name}, someone is interested in you. Send YES to confirm.")

        return (
            f"{target_user.name} ({target_user.age} years) from {target_user.town}.\n"
            f"Education: {user_details.level_of_education}, Profession: {user_details.profession}, "
            f"Marital: {user_details.marital_status}, Religion: {user_details.religion}, Ethnicity: {user_details.ethnicity}.\n"
            f"Send DESCRIBE {target_phone} to know more."
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
    elif user_input.startswith("describe"):
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

    # 🟢 MESSAGE <phone_number>#<content>
    elif user_input.startswith("message#"):
        try:
            _, target_phone, content = user_input.split("#", 2)
        except ValueError:
            return "Invalid format. Use: message#phone_number#content"

        target_user = get_user_by_phone(target_phone)
        if not target_user:
            return "User not found."

        # Ensure mutual approval before messaging
        approved_match = Match.query.filter_by(phone_number=phone_number, target_phone=target_phone, status="approved").first()
        if not approved_match:
            return "You can only message users who have mutually approved you."

        save_message(target_phone, content, is_system_message=False)
        return "Message sent successfully."

    # 🟢 Default Invalid Command
    else:
        return "Invalid command. Try again."

# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
