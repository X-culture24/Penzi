import os
import datetime
from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, UserDetails, SelfDescription, MatchRequest, Match, Message, ApprovalRequest

routes_bp = Blueprint("routes", __name__)

bcrypt = Bcrypt()  # ✅ Initialize Bcrypt


# ✅ Home Route
@routes_bp.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to Penzi Dating Service!"})


# ✅ 1. User Registration (With Password Hashing)
@routes_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json

    required_fields = ["name", "age", "gender", "county", "town", "phone_number", "password"]
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    new_user = User(
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        county=data["county"],
        town=data["town"],
        phone_number=data["phone_number"],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"Profile created successfully for {data['name']}!"})


# ✅ 2. User Login (Generates JWT Token)
@routes_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not all(key in data for key in ["phone_number", "password"]):
        return jsonify({"error": "Phone number and password required"}), 400

    user = User.query.filter_by(phone_number=data["phone_number"]).first()

    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid phone number or password"}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(days=1))

    return jsonify({
        "message": "Login successful!",
        "token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "phone_number": user.phone_number
        }
    })


# ✅ 3. Add User Details (Fetching user_id from JWT) - 🔥 FIXED ISSUE 🔥

@routes_bp.route("/user/details", methods=["POST"])
@jwt_required()
def add_user_details():
    user_id = get_jwt_identity()
    data = request.json

    required_fields = ["level_of_education", "profession", "marital_status", "religion", "ethnicity"]
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # ✅ Convert religion to lowercase to match ENUM values
    allowed_religions = {"christianity", "islam", "hinduism", "buddhism", "atheism"}
    religion = data["religion"].lower()

    if religion not in allowed_religions:
        return jsonify({"error": f"Invalid religion: {data['religion']}. Allowed values: {list(allowed_religions)}"}), 400

    new_details = UserDetails(
        user_id=user_id,
        level_of_education=data["level_of_education"],
        profession=data["profession"],
        marital_status=data["marital_status"],
        religion=religion,  # ✅ Save lowercase value
        ethnicity=data["ethnicity"]
    )

    db.session.add(new_details)
    db.session.commit()

    return jsonify({"message": "Additional details saved successfully!"})



@routes_bp.route("/user/self-description", methods=["OPTIONS", "POST"])
@jwt_required()
def add_self_description():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200  # ✅ Handle preflight request

    try:
        user_id = get_jwt_identity()
        data = request.json

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        description = data.get("description")
        if not description:
            return jsonify({"error": "Missing description"}), 400

        existing_description = SelfDescription.query.filter_by(user_id=user_id).first()
        if existing_description:
            return jsonify({"error": "Self-description already exists. Update instead."}), 409

        new_description = SelfDescription(user_id=user_id, description=description)
        db.session.add(new_description)
        db.session.commit()

        return jsonify({"message": "Self-description saved successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@routes_bp.route("/match/request", methods=["POST"])
@jwt_required()
def request_match():
    user_id = get_jwt_identity()
    data = request.json

    if not all(key in data for key in ["age_range", "town"]):
        return jsonify({"error": "Missing required fields"}), 400

    min_age, max_age = map(int, data["age_range"].split("-"))
    town = data["town"]

    # Get user's gender
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    print(f"🔍 Searching for matches between ages {min_age}-{max_age} in {town}, excluding gender: {current_user.gender}")

    # Find potential matches of the opposite gender
    matches = User.query.filter(
        User.age.between(min_age, max_age),
        User.town.ilike(town),
        User.gender != current_user.gender
    ).all()

    if not matches:
        print("🚫 No matches found!")
        return jsonify({"message": "No matches found"}), 404

    # Store match IDs and reset offset
    session["match_results"] = [m.id for m in matches]
    session["last_match_offset"] = 0

    print("🗂️ Stored match IDs:", session["match_results"])

    # Fetch the first 3 matches
    first_batch = matches[:3]
    session["last_match_offset"] = 3

    return format_match_response(first_batch, len(matches), offset=3)


@routes_bp.route("/match/next", methods=["GET"])
@jwt_required()
def get_more_matches():
    user_id = get_jwt_identity()
    match_ids = session.get("match_results", [])
    offset = session.get("last_match_offset", 0)

    print("📊 Current match IDs in session:", match_ids)
    print("➡️ Current offset:", offset)

    if not match_ids or offset >= len(match_ids):
        return jsonify({"message": "No more matches available."}), 404

    # Fetch next 3 matches
    next_offset = offset + 3
    next_batch_ids = match_ids[offset:next_offset]
    matches = User.query.filter(User.id.in_(next_batch_ids)).all()

    # Update the offset in session
    session["last_match_offset"] = next_offset

    return format_match_response(matches, len(match_ids), offset=next_offset)


# ✅ Helper: Format Match Response (Updated to include match_id)
def format_match_response(matches, total_matches, offset):
    match_list = [
        {
            "match_id": m.id,  # ✅ Include match_id for approval
            "name": m.name,
            "age": m.age,
            "phone_number": m.phone_number
        }
        for m in matches
    ]

    remaining = total_matches - offset
    next_message = f"Send 'NEXT' to receive details of the remaining {remaining} matches." if remaining > 0 else "No more matches available."

    return jsonify({
        "message": f"We found {total_matches} potential matches!",
        "matches": match_list,
        "next_message": next_message
    })


# ✅ 7. Describe Match (Detailed Info)
@routes_bp.route("/match/describe/<phone_number>", methods=["GET"])
@jwt_required()
def describe_match(phone_number):
    user_id = get_jwt_identity()

    # Find the user by phone number
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    user_details = UserDetails.query.filter_by(user_id=user.id).first()
    description = SelfDescription.query.filter_by(user_id=user.id).first()

    if not user_details or not description:
        return jsonify({"error": "Incomplete profile information."}), 404

    # Send detailed match info
    match_info = {
        "name": user.name,
        "age": user.age,
        "county": user.county,
        "town": user.town,
        "education": user_details.level_of_education,
        "profession": user_details.profession,
        "marital_status": user_details.marital_status,
        "religion": user_details.religion,
        "ethnicity": user_details.ethnicity,
        "description": description.description
    }

    # Notify the matched user (simulated message)
    notify_matched_user(user, user_id)

    return jsonify({"match_details": match_info})


# ✅ Helper: Notify Matched User
def notify_matched_user(matched_user, requester_id):
    requester = User.query.get(requester_id)
    if requester:
        print(f"📩 Notification sent to {matched_user.phone_number}:")
        print(f"Hi {matched_user.name}, {requester.name} is interested in you. Send 'YES' to 22141 to connect.")
    

# ✅ 8. Approve Match
@routes_bp.route("/approve", methods=["POST"])
@jwt_required()
def approve_match():
    user_id = get_jwt_identity()  # Current user approving the match
    data = request.json

    if "matched_user_id" not in data:
        return jsonify({"error": "Matched user ID is required."}), 400

    matched_user = User.query.get(data["matched_user_id"])
    if not matched_user:
        return jsonify({"error": "Matched user not found."}), 404

    # Ensure no duplicate approval exists
    existing_approval = ApprovalRequest.query.filter_by(
        matched_user_id=data["matched_user_id"],
        requesting_user_id=user_id
    ).first()

    if existing_approval:
        return jsonify({"error": "Approval request already exists."}), 409

    # Create and store the approval request
    new_approval = ApprovalRequest(
        matched_user_id=data["matched_user_id"],
        requesting_user_id=user_id,
        status="Pending"
    )

    db.session.add(new_approval)
    db.session.commit()

    # Notify the matched user
    notify_matched_user(matched_user, user_id)

    return jsonify({"message": "Match approved successfully!"}), 201

@routes_bp.route("/message/send", methods=["POST"])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.json

    if "to_user_id" not in data or "message_content" not in data:
        return jsonify({"error": "Recipient ID and message content are required."}), 400

    recipient = User.query.get(data["to_user_id"])
    if not recipient:
        return jsonify({"error": "Recipient not found."}), 404

    if not data["message_content"].strip():
        return jsonify({"error": "Message content cannot be empty."}), 400

    # Create and save the message without approval check
    new_message = Message(
        from_user_id=user_id,
        to_user_id=data["to_user_id"],
        message_content=data["message_content"]
    )

    db.session.add(new_message)
    db.session.commit()

    print(f"📤 Message sent from {user_id} to {data['to_user_id']}: {data['message_content']}")

    return jsonify({"message": "Message sent successfully!"}), 201


@routes_bp.route("/message/history/<int:to_user_id>", methods=["GET"])
@jwt_required()
def get_message_history(to_user_id):
    user_id = get_jwt_identity()

    # Ensure the recipient exists
    recipient = User.query.get(to_user_id)
    if not recipient:
        return jsonify({"error": "Recipient not found."}), 404

    # Retrieve messages between the two users
    messages = Message.query.filter(
        ((Message.from_user_id == user_id) & (Message.to_user_id == to_user_id)) |
        ((Message.from_user_id == to_user_id) & (Message.to_user_id == user_id))
    ).order_by(Message.timestamp.asc()).all()

    message_history = [
        {
            "from_user_id": msg.from_user_id,
            "to_user_id": msg.to_user_id,
            "message_content": msg.message_content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in messages
    ]

    return jsonify({"messages": message_history}), 200



# ✅ 9. Logout Route (Clears JWT Token)
@routes_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    session.clear()  # Clears session data
    return jsonify({"message": "Logged out successfully!"})
