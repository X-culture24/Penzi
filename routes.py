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



# ✅ 5. Match Request (Return First 3 Matches)
@routes_bp.route("/match/request", methods=["POST"])
@jwt_required()
def request_match():
    user_id = get_jwt_identity()
    data = request.json

    if not all(key in data for key in ["age_range", "town"]):
        return jsonify({"error": "Missing required fields"}), 400

    min_age, max_age = map(int, data["age_range"].split("-"))

    matches = User.query.filter(
        User.age.between(min_age, max_age),
        User.town.ilike(data["town"])
    ).limit(3).all()

    if not matches:
        return jsonify({"message": "No matches found"}), 404

    session["last_match_offset"] = 3
    match_list = [{"name": m.name, "age": m.age, "phone_number": m.phone_number} for m in matches]

    return jsonify({
        "matches": match_list,
        "next_message": "Send 'NEXT' to receive more matches."
    })


# ✅ 6. Retrieve More Matches (NEXT)
@routes_bp.route("/match/next", methods=["GET"])
@jwt_required()
def get_more_matches():
    user_id = get_jwt_identity()
    offset = session.get("last_match_offset", 0)

    match_request = MatchRequest.query.filter_by(user_id=user_id).first()
    if not match_request:
        return jsonify({"message": "No previous match request found."}), 400

    min_age, max_age = map(int, match_request.age_range.split("-"))
    matches = User.query.filter(
        User.age.between(min_age, max_age),
        User.town.ilike(match_request.town)
    ).offset(offset).limit(3).all()

    if not matches:
        return jsonify({"message": "No more matches available."})

    session["last_match_offset"] = offset + 3
    match_list = [{"name": m.name, "age": m.age, "phone_number": m.phone_number} for m in matches]

    return jsonify({
        "matches": match_list,
        "next_message": "Send 'NEXT' to receive more matches." if len(matches) == 3 else "No more matches available."
    })


# ✅ 7. Send Message
@routes_bp.route("/message", methods=["POST"])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.json

    required_fields = ["receiver_id", "content"]
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_message = Message(
        sender_id=user_id,
        receiver_id=data["receiver_id"],
        content=data["content"]
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({"message": "Message sent successfully!"})


# ✅ 8. Approve Match
@routes_bp.route("/approve", methods=["POST"])
@jwt_required()
def approve_match():
    user_id = get_jwt_identity()
    data = request.json

    if "match_id" not in data:
        return jsonify({"error": "Match ID is required"}), 400

    new_approval = ApprovalRequest(user_id=user_id, match_id=data["match_id"])

    db.session.add(new_approval)
    db.session.commit()

    return jsonify({"message": "Match approved successfully!"})


# ✅ 9. Logout Route (Clears JWT Token)
@routes_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    session.clear()  # Clears session data
    return jsonify({"message": "Logged out successfully!"})
