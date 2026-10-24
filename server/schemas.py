from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    password_confirmation = fields.Str(required=True)

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("password_confirmation"):
            raise ValidationError("Password and confirmation do not match.", "password_confirmation")


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class NoteCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    content = fields.Str(required=True, validate=validate.Length(min=1))


class NoteUpdateSchema(Schema):
    """PATCH: every field is optional, but at least one must be supplied."""
    title = fields.Str(validate=validate.Length(min=1, max=120))
    content = fields.Str(validate=validate.Length(min=1))

    @validates_schema
    def at_least_one(self, data, **kwargs):
        if not data:
            raise ValidationError("Provide at least one of: title, content.")


def format_errors(messages):
    """Flatten marshmallow's {field: [msgs]} into the list of strings the client renders."""
    errors = []
    for field, msgs in messages.items():
        for msg in msgs if isinstance(msgs, list) else [msgs]:
            errors.append(msg if field == "_schema" else f"{field}: {msg}")
    return errors
