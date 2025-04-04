from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    county = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    
    # Relationships
    details = relationship("UserDetails", back_populates="user", uselist=False)
    description = relationship("SelfDescription", back_populates="user", uselist=False)
    match_requests = relationship("MatchRequest", back_populates="user")
    matches_as_target = relationship("Match", 
                                   foreign_keys="Match.matched_user_id",
                                   back_populates="matched_user")
    sent_messages = relationship("Message", 
                               foreign_keys="Message.from_user_id",
                               back_populates="from_user")
    received_messages = relationship("Message",
                                   foreign_keys="Message.to_user_id",
                                   back_populates="to_user")
    sent_approvals = relationship("ApprovalRequest",
                                foreign_keys="ApprovalRequest.requesting_user_id",
                                back_populates="requesting_user")
    received_approvals = relationship("ApprovalRequest",
                                    foreign_keys="ApprovalRequest.matched_user_id",
                                    back_populates="matched_user")

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_of_education = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    marital_status = db.Column(db.String(20), nullable=False)
    religion = db.Column(db.String(50), nullable=False)
    ethnicity = db.Column(db.String(100), nullable=False)
    
    user = relationship("User", back_populates="details")

class SelfDescription(db.Model):
    __tablename__ = 'self_description'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    user = relationship("User", back_populates="description")

class MatchRequest(db.Model):
    __tablename__ = 'match_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age_range = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    
    user = relationship("User", back_populates="match_requests")
    matches = relationship("Match", back_populates="request")

class Match(db.Model):
    __tablename__ = 'match'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('match_request.id'), nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)  # Made non-nullable
    target_phone = db.Column(db.String(20), nullable=False)  # Made non-nullable
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())  # Added timestamp
    
    # Relationships with explicit cascade rules
    request = db.relationship(
        "MatchRequest", 
        back_populates="matches",
        foreign_keys=[request_id]
    )
    
    matched_user = db.relationship(
        "User",
        foreign_keys=[matched_user_id],
        back_populates="matches_as_target"
    )
    
    # Add index for better performance on frequent queries
    __table_args__ = (
        db.Index('idx_match_phone', 'phone_number'),
        db.Index('idx_match_target', 'target_phone'),
        db.Index('idx_match_status', 'status'),
    )
class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    message_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_messages")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_messages")

class ApprovalRequest(db.Model):
    __tablename__ = 'approval_request'
    
    id = db.Column(db.Integer, primary_key=True)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requesting_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    
    matched_user = relationship("User", foreign_keys=[matched_user_id], back_populates="received_approvals")
    requesting_user = relationship("User", foreign_keys=[requesting_user_id], back_populates="sent_approvals")