from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func

db = SQLAlchemy()

# ✅ Users Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # ✅ Now a String instead of ENUM
    county = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# ✅ UserDetails Table
class UserDetails(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    level_of_education = Column(String(100), nullable=False)
    profession = Column(String(100), nullable=False)
    marital_status = Column(String(20), nullable=False)  # ✅ Changed ENUM to String
    religion = Column(String(50), nullable=False)  # ✅ Changed ENUM to String
    ethnicity = Column(String(100), nullable=False)


# ✅ SelfDescription Table
class SelfDescription(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    description = Column(Text, nullable=False)


# ✅ MatchRequests Table
class MatchRequest(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    age_range = Column(String(50), nullable=False)  # Example: "23-25"
    town = Column(String(100), nullable=False)


# ✅ Matches Table
class Match(db.Model):
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("match_request.id"), nullable=False)
    matched_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)


# ✅ Messages Table
class Message(db.Model):
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())


# ✅ ApprovalRequests Table
class ApprovalRequest(db.Model):
    id = Column(Integer, primary_key=True)
    matched_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    requesting_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    status = Column(String(20), default="Pending", nullable=False)  # ✅ Changed ENUM to String
