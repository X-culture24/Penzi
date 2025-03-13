import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, UserDetails, SelfDescription, Match, Message

app = Flask(__name__)

# ✅ Set a Secret Key (required for session)
app.secret_key = os.urandom(24)
# ✅ Enable CORS
CORS(app)

# ✅ Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Helper: Save Message to Database
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

# ✅ Main API Endpoint (One URL for All Operations)
@app.route("/penzi", methods=["POST"])
def penzi_chatbot():
    data = request.json
    phone_number = data.get("phone_number")
    user_input = data.get("message")

    if not phone_number or not user_input:
        return jsonify({"error": "phone_number and message are required"}), 400

    user = get_user_by_phone(phone_number)

    save_message(phone_number, user_input, is_system_message=False)

    response = process_user_input(user, user_input, phone_number)

    save_message(phone_number, response, is_system_message=True)

    return jsonify({"response": response})

# ✅ Helper: Process User Input
def process_user_input(user, user_input, phone_number):
    user_input = user_input.lower().strip()

    # 🟢 Activation
    if user_input == "penzi":
        return "Welcome to Penzi! To register, send: start#name#age#gender#county#town."

    # 🟢 Registration
    elif user_input.startswith("start#"):
        try:
            _, name, age, gender, county, town = user_input.split("#")
            age = int(age)
        except ValueError:
            return "Invalid format. Please send: start#name#age#gender#county#town."

        if user:
            return "You are already registered."

        new_user = User(
            name=name,
            age=age,
            gender=gender,
            county=county,
            town=town,
            phone_number=phone_number
        )
        db.session.add(new_user)
        db.session.commit()

        return f"Welcome, {name}! Now send: details#education#profession#maritalStatus#religion#ethnicity."

    # 🟢 User Details
    elif user_input.startswith("details#"):
        if not user:
            return "Please register first by sending: start#name#age#gender#county#town."

        try:
            _, education, profession, marital_status, religion, ethnicity = user_input.split("#")
        except ValueError:
            return "Invalid format. Use: details#education#profession#maritalStatus#religion#ethnicity."

        user_details = UserDetails(
            user_id=user.id,
            level_of_education=education,
            profession=profession,
            marital_status=marital_status,
            religion=religion,
            ethnicity=ethnicity
        )
        db.session.add(user_details)
        db.session.commit()

        return "Details saved! Send: myself#description to describe yourself."

    # 🟢 Self-Description
    elif user_input.startswith("myself#"):
        if not user:
            return "Register first: start#name#age#gender#county#town."

        description = user_input.replace("myself#", "").strip()
        if not description:
            return "Please provide a description."

        self_description = SelfDescription(
            user_id=user.id,
            description=description
        )
        db.session.add(self_description)
        db.session.commit()

        return "Self-description saved! Send: match#ageRange#town to find matches."

    # 🟢 Match Request
    elif user_input.startswith("match#"):
        if not user:
            return "Register first: start#name#age#gender#county#town."

        try:
            _, age_range, town = user_input.split("#")
            min_age, max_age = map(int, age_range.split("-"))
        except ValueError:
            return "Invalid format. Use: match#ageRange#town."

        matches = User.query.filter(
            User.age.between(min_age, max_age),
            User.town.ilike(town),
            User.gender != user.gender
        ).all()

        if not matches:
            return "No matches found."

        session["matches"] = [m.id for m in matches]
        session["match_offset"] = 0

        first_batch = matches[:3]
        session["match_offset"] = 3

        match_list = [
            f"{m.name}, aged {m.age}, from {m.town}"
            for m in first_batch
        ]
        return f"We found {len(matches)} matches! Here are the first 3:\n" + "\n".join(match_list) + "\nSend NEXT for more."

    # 🟢 Next Matches
    elif user_input == "next":
        match_ids = session.get("matches", [])
        offset = session.get("match_offset", 0)

        if not match_ids or offset >= len(match_ids):
            return "No more matches available."

        next_batch_ids = match_ids[offset:offset + 3]
        matches = User.query.filter(User.id.in_(next_batch_ids)).all()

        session["match_offset"] = offset + 3

        match_list = [
            f"{m.name}, aged {m.age}, from {m.town}"
            for m in matches
        ]
        return "Next matches:\n" + "\n".join(match_list)

    else:
        return "Invalid command. Try again."

# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
