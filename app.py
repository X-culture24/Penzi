import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, UserDetails, SelfDescription, Match, Message ,MatchRequest
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
load_dotenv()
app.secret_key = os.urandom(24)
CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

# Helper Functions
def save_message(from_user_id, to_user_id, message_content):
    new_message = Message(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        message_content=message_content
    )
    db.session.add(new_message)
    db.session.commit()
    return new_message

def get_user_by_phone(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()

def notify_user(target_phone, content):
    print(f"📢 Notification to {target_phone}: {content}")

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

def create_match(phone_number, user_input):
    # First get or create the necessary related records
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return False
    
    # Create or get a MatchRequest
    match_request = MatchRequest.query.filter_by(user_id=user.id).first()
    if not match_request:
        match_request = MatchRequest(
            user_id=user.id,
            age_range="25-30",  # Set appropriate values
            town="Nairobi"       # Set appropriate values
        )
        db.session.add(match_request)
        db.session.commit()
    
    # Get the matched user (you need logic to determine this)
    matched_user = User.query.filter_by(phone_number=user_input).first()
    if not matched_user:
        return False
    
    # Now create the Match with all required fields
    new_match = Match(
        request_id=match_request.id,
        matched_user_id=matched_user.id,
        phone_number=phone_number,
        target_phone=user_input,
        status='pending'
    )
    
    db.session.add(new_match)
    db.session.commit()
    return True

# Main Chatbot Endpoint
@app.route("/penzi", methods=["POST"])
def penzi_chatbot():
    data = request.json
    phone_number = data.get("phone_number")
    user_input = data.get("message")

    if not phone_number or not user_input:
        return jsonify({"error": "phone_number and message are required"}), 400

    user = get_user_by_phone(phone_number)
    if user:
        save_message(user.id, None, user_input)

    response = process_user_input(user, user_input, phone_number)
    
    if user:
        save_message(None, user.id, response)

    return jsonify({"response": response})

def process_user_input(user, user_input, phone_number):
    user_input = user_input.strip().upper()  # Normalize input to uppercase

    # Activation Command
    if user_input == "PENZI":
        if user:
            return "You are already registered. To search, SMS: match#age#town (e.g., match#23-25#Kisumu)"
        return "Welcome! To register SMS: start#name#age#gender#county#town (e.g., start#John#26#Male#Nairobi#Westlands)"

    # User Registration
    elif user_input.startswith("START#"):
        if user:
            return "You are already registered. To search, SMS: match#age#town"
            
        try:
            _, name, age, gender, county, town = user_input.split("#")
            age = int(age)
            user = create_new_user(phone_number, name, age, gender, county, town)
            return f"Profile created {name}. SMS: details#education#profession#status#religion#ethnicity (e.g., details#degree#engineer#single#christian#kikuyu)"
        except:
            return "Invalid format. Use: start#name#age#gender#county#town"

    # Details Registration
    elif user_input.startswith("DETAILS#"):
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        try:
            _, education, profession, status, religion, ethnicity = user_input.split("#")
            details = UserDetails(
                user_id=user.id,
                level_of_education=education,
                profession=profession,
                marital_status=status,
                religion=religion,
                ethnicity=ethnicity
            )
            db.session.add(details)
            db.session.commit()
            return "Final step: SMS your self-description starting with MYSELF (e.g., MYSELF friendly, adventurous)"
        except:
            return "Invalid format. Use: details#education#profession#status#religion#ethnicity"

    # Self Description
    elif user_input.startswith("MYSELF"):
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        description = user_input[6:].strip()
        self_desc = SelfDescription(user_id=user.id, description=description)
        db.session.add(self_desc)
        db.session.commit()
        return "Registration complete! To search for matches, SMS: match#age-range#town (e.g., match#25-30#Nairobi)"

    # Match Request
    elif user_input.startswith("MATCH#"):
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        try:
            _, age_range, town = user_input.split("#")
            session.setdefault("match_offset", 0)
            matches = get_matches(user, age_range, town, session["match_offset"])

            if not matches:
                session.pop("match_offset", None)
                return "No matches found. Try different criteria."

            session["match_offset"] += 3
            match_list = "\n".join(f"{m.name} {m.age}yrs, {m.phone_number}" for m in matches)
            return f"Matches:\n{match_list}\n\nFor details SMS: DETAILS phone (e.g., DETAILS 0712345678)"
        except:
            return "Invalid format. Use: match#minage-maxage#town (e.g., match#25-30#Nairobi)"

    # DETAILS command - Returns profile details
    elif user_input.startswith("DETAILS"):
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        try:
            _, target_phone = user_input.split()
            target_user = get_user_by_phone(target_phone)
            if not target_user:
                return "User not found."

            user_details = UserDetails.query.filter_by(user_id=target_user.id).first()
            if not user_details:
                return "No details available for this user."

            notify_user(target_phone, f"{user.name} viewed your profile")
            
            response = (
                f"{target_user.name}'s Details:\n"
                f"Education: {user_details.level_of_education}\n"
                f"Profession: {user_details.profession}\n"
                f"Status: {user_details.marital_status}\n"
                f"Religion: {user_details.religion}\n"
                f"Ethnicity: {user_details.ethnicity}\n\n"
                f"For their self-description, SMS: DESCRIBE {target_phone}"
            )
            
            # After showing details, suggest expressing interest
            response += "\n\nTo express interest, SMS the phone number alone (e.g., 0712345678)"
            return response
        except:
            return "Invalid format. Use: DETAILS phone (e.g., DETAILS 0712345678)"

    # DESCRIBE command - Returns self-description
    elif user_input.startswith("DESCRIBE"):
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        try:
            _, target_phone = user_input.split()
            target_user = get_user_by_phone(target_phone)
            if not target_user:
                return "User not found."

            description = SelfDescription.query.filter_by(user_id=target_user.id).first()
            if not description:
                return "No self-description available."

            response = f"{target_user.name} describes themselves as: {description.description}"
            
            # After showing description, suggest expressing interest
            response += "\n\nTo express interest, SMS the phone number alone (e.g., 0712345678)"
            return response
        except:
            return "Invalid format. Use: DESCRIBE phone (e.g., DESCRIBE 0712345678)"

    # Phone number lookup (expressing interest)
    elif user_input.isdigit() and len(user_input) == 10:
        if not user:
            return "Register first with: start#name#age#gender#county#town"

        target_user = get_user_by_phone(user_input)
        if not target_user:
            return "User not found."

        # Create match record
        create_match(phone_number, user_input)
        
        notify_user(user_input, f"{user.name} is interested in you! SMS YES to connect")
        return "Interest noted! We've notified them. You'll be connected if they respond YES."

    # YES command (accepting a match)
    elif user_input == "YES":
        # Find pending matches where this user is the target
        pending_matches = Match.query.filter_by(
            target_phone=phone_number,
            status="pending"
        ).all()

        if pending_matches:
            # Update all pending matches to approved
            for match in pending_matches:
                match.status = "approved"
                
                # Get user details for notification
                interested_user = get_user_by_phone(match.phone_number)
                if interested_user:
                    notify_user(match.phone_number, 
                              f"Match confirmed with {user.name}! You can now message each other")
                    notify_user(phone_number, 
                              f"Match confirmed with {interested_user.name}! You can now message each other")
            
            db.session.commit()
            return "Match confirmed! You can now message each other"
        
        return "No pending matches found"

    # Invalid command
    else:
        return (
            "Invalid command. Available commands:\n"
            "start#name#age#gender#county#town - Register\n"
            "details#education#profession#status#religion#ethnicity - Add details\n"
            "MYSELF description - Add self-description\n"
            "match#age-range#town - Find matches\n"
            "DETAILS phone - View someone's details\n"
            "DESCRIBE phone - View someone's self-description\n"
            "SMS a phone number alone to express interest\n"
            "SMS YES to accept a match"
        )

def get_matches(user, age_range, town, offset):
    try:
        min_age, max_age = map(int, age_range.split("-"))
        opposite_gender = "Male" if user.gender == "Female" else "Female"
        return User.query.filter(
            User.gender == opposite_gender,
            User.age >= min_age,
            User.age <= max_age,
            User.town.ilike(f"%{town}%"),
            User.id != user.id
        ).offset(offset).limit(3).all()
    except:
        return []

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)