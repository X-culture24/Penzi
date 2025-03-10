from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import User, db

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    phone_number = data.get("phone_number")

    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"message": "Phone number already registered"}), 400

    new_user = User(
        phone_number=phone_number,
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        county=data["county"],
        town=data["town"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(phone_number=data.get("phone_number")).first()

    if user and check_password_hash(user.password, data.get("password")):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"message": "Invalid credentials"}), 401
