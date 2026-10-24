from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from models import Note
from schemas import NoteCreateSchema, NoteUpdateSchema, format_errors

MAX_PER_PAGE = 100


def current_user_id():
    return int(get_jwt_identity())


def get_owned_note(note_id):
    """Return the note only if it belongs to the current user.

    Filtering by user_id means another user's note is indistinguishable from a
    missing one, so we answer 404 and never reveal that it exists.
    """
    return Note.query.filter_by(id=note_id, user_id=current_user_id()).first()


class NoteList(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        if page < 1 or per_page < 1:
            return {"errors": ["page and per_page must be positive integers."]}, 400
        per_page = min(per_page, MAX_PER_PAGE)

        pagination = (
            Note.query.filter_by(user_id=current_user_id())
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "notes": [n.to_dict() for n in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }, 200

    def post(self):
        try:
            data = NoteCreateSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": format_errors(err.messages)}, 422

        note = Note(title=data["title"].strip(), content=data["content"], user_id=current_user_id())
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteDetail(Resource):
    method_decorators = [jwt_required()]

    def get(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        return note.to_dict(), 200

    def patch(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        try:
            data = NoteUpdateSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": format_errors(err.messages)}, 422

        for field, value in data.items():
            setattr(note, field, value.strip() if field == "title" else value)
        db.session.commit()
        return note.to_dict(), 200

    def delete(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        db.session.delete(note)
        db.session.commit()
        return "", 204
