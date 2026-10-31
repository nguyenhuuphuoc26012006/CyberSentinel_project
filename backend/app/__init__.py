import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db
from .api import api_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://cyber_user:change_this_local_password@localhost:5432/cybersentinel",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(app, resources={r"/api/*": {"origins": origins}})

    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Starter convenience for local development. Replace with Alembic migrations
    # before treating the application as production software.
    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
