import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message

app = Flask(__name__)

# ✅ Secret Key (for session handling)
app.secret_key = os.urandom(24)

# ✅ Enable CORS
CORS(app)

# ✅ Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize DB and Migrations
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Helper: Save Message
def save_message(phone_number, content, is_system_message=False):
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        print(f"❌ User not found for phone number: {phone_number}")
        return None

    new_message = Message(
        from_user_id=user.id,
        to_user_id=None,
        message_content=content,
    )
    db.session.add(new_message)
    db.session.commit()
    print(f"✅ Message saved: {content}")
    return new_message

# ✅ Helper: Get User by Phone Number
def get_user_by_phone(phone_number):
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        print(f"✅ User found: {user.phone_number}")
    else:
        print(f"❌ No user found for {phone_number}")
    return user

# ✅ Helper: Notify User
def notify_user(target_phone, content):
    save_message(target_phone, content, is_system_message=True)

# ✅ Main Endpoint
@app.route("/penzi", methods=["POST"])
def penzi_chatbot():
    data = request.json
    print(f"📥 Incoming request: {data}")

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

    # 🟢 MOREDETAILS <phone_number>
    elif user_input.startswith("moredetails"):
        try:
            _, target_phone = user_input.split(" ")
        except ValueError:
            print("❌ Invalid MOREDETAILS format.")
            return "Invalid format. Use: MOREDETAILS <phone_number>"

        target_user = get_user_by_phone(target_phone)
        if not target_user:
            return "User not found."

        user_details = UserDetails.query.filter_by(user_id=target_user.id).first()
        if not user_details:
            return f"No details available for {target_user.name}."

        # Notify the Requested User
        notify_user(target_phone, f"Hi {target_user.name}, someone is interested in you. Send YES to know more!")

        return (
            f"{target_user.name} ({target_user.age} years) from {target_user.town}.\n"
            f"Education: {user_details.level_of_education}, Profession: {user_details.profession}, "
            f"Marital: {user_details.marital_status}, Religion: {user_details.religion}, Ethnicity: {user_details.ethnicity}.\n"
            f"Send DESCRIBE {target_phone} to know more."
        )

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

    # 🟢 Default Invalid Command
    else:
        print("❌ Unknown command.")
        return "Invalid command. Try again."

# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
