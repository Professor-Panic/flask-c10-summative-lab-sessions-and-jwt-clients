from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User
from schemas import LoginSchema, SignupSchema, format_errors


def make_auth_response(user, status):
    # JWT subject must be a string in newer PyJWT versions; we convert back with int() on read.
    token = create_access_token(identity=str(user.id))
    return {"token": token, "user": user.to_dict()}, status


class Signup(Resource):
    def post(self):
        try:
            data = SignupSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": format_errors(err.messages)}, 422

        if User.query.filter(db.func.lower(User.username) == data["username"].strip().lower()).first():
            return {"errors": ["Username is already taken."]}, 422

        user = User(username=data["username"])
        user.password_hash = data["password"]
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        return make_auth_response(user, 201)


class Login(Resource):
    def post(self):
        try:
            data = LoginSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": format_errors(err.messages)}, 422

        user = User.query.filter_by(username=data["username"].strip()).first()
        # Same message for unknown user and bad password so usernames can't be probed.
        if not user or not user.authenticate(data["password"]):
            return {"errors": ["Invalid username or password."]}, 401

        return make_auth_response(user, 200)


class Me(Resource):
    @jwt_required()
    def get(self):
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return {"errors": ["User not found."]}, 401
        return user.to_dict(), 200
