from flask import Blueprint, request, jsonify, session
from models import db, User, UserDetails, SelfDescription, MatchRequest, Match, Message, ApprovalRequest

routes_bp = Blueprint("routes", __name__)

# ✅ Home Route
@routes_bp.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to Penzi Dating Service!"})


# ✅ 1. User Registration
@routes_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json

    if not all(key in data for key in ["name", "age", "gender", "county", "town", "phone_number"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_user = User(
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        county=data["county"],
        town=data["town"],
        phone_number=data["phone_number"]
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"Profile created successfully for {data['name']}!"})


# ✅ 2. Add User Details
@routes_bp.route("/user/details", methods=["POST"])
def add_user_details():
    data = request.json

    if not all(key in data for key in ["user_id", "level_of_education", "profession", "marital_status", "religion", "ethnicity"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_details = UserDetails(
        user_id=data["user_id"],
        level_of_education=data["level_of_education"],
        profession=data["profession"],
        marital_status=data["marital_status"],
        religion=data["religion"],
        ethnicity=data["ethnicity"]
    )

    db.session.add(new_details)
    db.session.commit()

    return jsonify({"message": "Additional details saved successfully!"})


# ✅ 3. Self-Description
@routes_bp.route("/user/self-description", methods=["POST"])
def add_self_description():
    data = request.json

    if not all(key in data for key in ["user_id", "description"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_description = SelfDescription(
        user_id=data["user_id"],
        description=data["description"]
    )

    db.session.add(new_description)
    db.session.commit()

    return jsonify({"message": "Self-description saved successfully!"})


# ✅ 4. Match Request (Return First 3 Matches)
@routes_bp.route("/match/request", methods=["POST"])
def request_match():
    data = request.json

    if not all(key in data for key in ["user_id", "age_range", "town"]):
        return jsonify({"error": "Missing required fields"}), 400

    min_age, max_age = map(int, data["age_range"].split("-"))
    town = data["town"]

    matches = User.query.filter(
        User.age.between(min_age, max_age),
        User.town.ilike(town)
    ).limit(3).all()

    if not matches:
        return jsonify({"message": "No matches found"}), 404

    session["last_match_offset"] = 3  # Track offset for next match request
    match_list = [{"name": m.name, "age": m.age, "phone_number": m.phone_number} for m in matches]

    return jsonify({
        "matches": match_list,
        "next_message": "Send 'NEXT' to receive more matches."
    })


# ✅ 5. Retrieve More Matches (NEXT)
@routes_bp.route("/match/next/<int:user_id>", methods=["GET"])
def get_more_matches(user_id):
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


# ✅ 6. Request Description (DESCRIBE <phone_number>)
@routes_bp.route("/describe/<string:phone_number>", methods=["GET"])
def describe_user(phone_number):
    user = User.query.filter_by(phone_number=phone_number).first()

    if not user:
        return jsonify({"error": "User not found."}), 404

    description = SelfDescription.query.filter_by(user_id=user.id).first()
    if not description:
        return jsonify({"message": f"{user.name} has not provided a self-description yet."})

    user_details = UserDetails.query.filter_by(user_id=user.id).first()
    details = {
        "name": user.name,
        "age": user.age,
        "county": user.county,
        "town": user.town,
        "education": user_details.level_of_education if user_details else "N/A",
        "profession": user_details.profession if user_details else "N/A",
        "marital_status": user_details.marital_status if user_details else "N/A",
        "religion": user_details.religion if user_details else "N/A",
        "ethnicity": user_details.ethnicity if user_details else "N/A",
        "description": description.description
    }

    return jsonify(details)


# ✅ 7. Approve Match
@routes_bp.route("/approve", methods=["POST"])
def approve_match():
    data = request.json

    if not all(key in data for key in ["matched_user_id", "requesting_user_id", "status"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_approval = ApprovalRequest(
        matched_user_id=data["matched_user_id"],
        requesting_user_id=data["requesting_user_id"],
        status=data["status"]
    )

    db.session.add(new_approval)
    db.session.commit()

    return jsonify({"message": "Approval request submitted!"})
