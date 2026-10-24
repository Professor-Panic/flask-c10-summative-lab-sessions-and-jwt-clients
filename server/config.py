import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-in-prod")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-in-prooooood")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    PROPAGATE_EXCEPTIONS = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
