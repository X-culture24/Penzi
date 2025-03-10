import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
from routes import routes_bp

app = Flask(__name__)

# ✅ Set Secret Key (Secure Method)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")  # Use env variable, fallback if not set

# ✅ Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Register Blueprint
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(debug=True)
