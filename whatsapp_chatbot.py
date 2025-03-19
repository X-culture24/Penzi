import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Configuration
app.secret_key = os.urandom(24)  # Secure Random Secret Key
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize Extensions
CORS(app)  # Enable Cross-Origin Resource Sharing
db.init_app(app)  # Initialize Database
migrate = Migrate(app, db)  # Enable Database Migrations


# ✅ Helper: Save Message to Database
def save_message(phone_number, content, is_system_message=False):
    """
    Stores messages (user/system) in the database.
    """
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return None

    message = Message(
        from_user_id=user.id,
        to_user_id=None,
        message_content=content,
    )
    db.session.add(message)
    db.session.commit()
    return message


# ✅ Helper: Get User by Phone Number
def get_user_by_phone(phone_number):
    """
    Fetches a user by their phone number.
    """
    return User.query.filter_by(phone_number=phone_number).first()


# ✅ Helper: Normalize Phone Number (+254 Format)
def normalize_phone_number(phone_number):
    """
    Ensures phone numbers follow the +254 format.
    """
    if phone_number.startswith("254"):
        return f"+{phone_number}"
    return phone_number


# ✅ WhatsApp Chatbot Endpoint
@app.route("/whatsapp", methods=["POST"])
def whatsapp_chatbot():
    """
    Main endpoint to handle WhatsApp messages.
    """
    data = request.json
    print(data)  # Log incoming WhatsApp payload

    phone_number = normalize_phone_number(data.get("from"))
    user_input = data.get("body")

    if not phone_number or not user_input:
        return jsonify({"error": "Invalid WhatsApp payload"}), 400

    # Fetch or create user
    user = get_user_by_phone(phone_number)

    # Save incoming user message
    save_message(phone_number, user_input, is_system_message=False)

    # Generate a chatbot response
    response = process_user_input(user, user_input, phone_number)

    # Save outgoing system response
    save_message(phone_number, response, is_system_message=True)

    return jsonify({
        "response": response,
        "to": phone_number,
        "from": "26657991016",
        "reply": response
    })


# ✅ Helper: Process User Input (Main Logic)
def process_user_input(user, user_input, phone_number):
    """
    Processes user input and handles different chatbot commands.
    """
    user_input = user_input.lower().strip()

    # 🟢 Activation
    if user_input == "penzi":
        if user:
            return (
                "Proceed with match requests. You are already registered.\n"
                "Send: match#ageRange#town to find matches.\n"
                "Example: match#25-35#Nairobi"
            )
        return "Welcome to Penzi! To register, send: start#name#age#gender#county#town."

    # 🟢 Match Request
    elif user_input.startswith("match#"):
        if not user:
            return "Register first: start#name#age#gender#county#town."
        return handle_match_request(user, user_input)

    # 🟢 Retrieve Next Matches
    elif user_input == "next":
        if not user:
            return "Register first to find matches."
        return get_next_matches(user)

    # 🟢 MOREDETAILS Command
    elif user_input.startswith("moredetails"):
        if not user:
            return "Register first: start#name#age#gender#county#town."
        return handle_more_details(user_input)

    # 🟢 Invalid Command
    else:
        return "Invalid command. Try again."


# ✅ Helper: Handle Match Request
def handle_match_request(user, user_input):
    """
    Processes 'match#ageRange#town' command.
    """
    try:
        _, age_range, town = user_input.split("#")
        min_age, max_age = map(int, age_range.split("-"))
    except ValueError:
        return "Invalid format. Use: match#ageRange#town. Example: match#25-35#Nairobi"

    # Match opposite gender
    opposite_gender = "male" if user.gender == "female" else "female"

    matches = User.query.filter(
        User.age.between(min_age, max_age),
        User.town.ilike(town),
        User.gender == opposite_gender,
        User.id != user.id
    ).all()

    if not matches:
        return "No matches found."

    # Store matches in session
    session["matches"] = [m.id for m in matches]
    session["match_offset"] = 0

    return get_next_matches(user)


# ✅ Helper: Get Next Matches (in batches of 3)
def get_next_matches(user):
    """
    Retrieves the next batch of 3 matches.
    """
    offset = session.get("match_offset", 0)
    matches = session.get("matches", [])

    if offset >= len(matches):
        return "No more matches available. Try a new search."

    next_batch = matches[offset:offset + 3]
    session["match_offset"] += 3

    match_info = []
    for match_id in next_batch:
        match_user = User.query.get(match_id)
        match_info.append(f"{match_user.name}, {match_user.age} years, {match_user.town}, Contact: {match_user.phone_number}")

    return "Here are your next matches:\n" + "\n".join(match_info) + "\nSend NEXT for more or MOREDETAILS <phone_number>."


# ✅ Helper: Handle MOREDETAILS Command
def handle_more_details(user_input):
    """
    Processes 'moredetails <phone_number>' command.
    """
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

    # Notify target user
    notify_message = f"Hi {target_user.name}, someone is interested in you. Reply YES to continue."
    save_message(target_user.phone_number, notify_message, is_system_message=True)

    return (
        f"{target_user.name} ({target_user.age} years) from {target_user.town}.\n"
        f"Education: {user_details.level_of_education}, Profession: {user_details.profession}, "
        f"Marital: {user_details.marital_status}, Religion: {user_details.religion}, "
        f"Ethnicity: {user_details.ethnicity}.\n"
        f"Send DESCRIBE {target_phone} to know more."
    )


# ✅ Run Flask Application
if __name__ == "__main__":
    app.run(port=5001, debug=True)  # Run on port 5001 for WhatsApp integration
