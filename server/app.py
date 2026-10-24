from flask import Flask
from flask_restful import Api

from auth import Login, Me, Signup
from config import Config
from extensions import bcrypt, db, jwt, migrate
from notes import NoteDetail, NoteList


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.compact = False

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    register_jwt_errors()

    api = Api(app)
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Me, "/me")
    api.add_resource(NoteList, "/notes")
    api.add_resource(NoteDetail, "/notes/<int:note_id>")
    return app


def register_jwt_errors():
    """Make every auth failure a 401 JSON body shaped like {"errors": [...]}."""

    @jwt.unauthorized_loader
    def missing_token(reason):
        return {"errors": ["Authentication required."]}, 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return {"errors": ["Invalid token."]}, 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return {"errors": ["Token has expired."]}, 401


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
