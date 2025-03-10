import os
from flask import Flask
from flask_cors import CORS  # Enable Cross-Origin Requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager  # ✅ Import JWT
from models import db
from routes import routes_bp  # ✅ Import routes, bcrypt is initialized there

app = Flask(__name__)

# ✅ Enable CORS
CORS(app)

# ✅ Set Secret Key (Secure Method)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")  # Use env variable, fallback if not set
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_jwt_key")  # ✅ JWT Secret Key

# ✅ Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)  # ✅ Initialize JWTManager

# ✅ Register Blueprint
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(debug=True)  # ✅ Ensure debug mode is ON
