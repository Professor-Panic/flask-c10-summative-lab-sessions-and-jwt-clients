# Notes API (Flask + JWT)

## Description
A secure RESTful Flask backend for a personal notes app. Users register and log in with a
username and password (hashed with Flask-Bcrypt) and receive a JWT (Flask-JWT-Extended).
Each user owns **Notes** (`title`, `content`) and can only see and change their own. The
included React client (`client/`) already handles signup, login and session persistence.

## Project structure
```
server/
  app.py         app factory, route registration, JWT error handlers
  config.py      configuration
  extensions.py  db, migrate, bcrypt, jwt instances
  models.py      User and Note models
  schemas.py     Marshmallow request validation
  auth.py        /signup, /login, /me
  notes.py       /notes CRUD + pagination
  seed.py        example data
  tests/         pytest suite
client/          provided React client (JWT version)
```

## Installation
```bash
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
flask db init        # first time only
flask db migrate -m "initial"
flask db upgrade
python seed.py       # optional example data
```
Seeded users: `alice`, `bob`, `carol`, all with password `password123`.

Set `SECRET_KEY` and `JWT_SECRET_KEY` environment variables outside development.

## Running
```bash
cd server
flask run -p 5555      # or: python app.py
```
The API listens on `http://localhost:5555`. To use the client:
```bash
cd client && npm install && npm start    # http://localhost:4000, proxies to port 5555
```

## Tests
```bash
cd server && python -m pytest
```

## Endpoints
Protected endpoints need the header `Authorization: Bearer <token>`.
Errors are JSON: `{"errors": ["message", ...]}`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/signup` | no | Body `username`, `password`, `password_confirmation`. Creates user, returns `{token, user}` (201). 422 on invalid input or taken username. |
| POST | `/login` | no | Body `username`, `password`. Returns `{token, user}` (200). 401 on bad credentials. |
| GET | `/me` | yes | Returns the current user `{id, username}`. 401 if token missing/invalid/expired. |
| GET | `/notes?page=1&per_page=10` | yes | Paginated list of your notes, newest first. Returns `notes, page, per_page, total, pages, has_next, has_prev` (`per_page` capped at 100). 400 on invalid paging values. |
| POST | `/notes` | yes | Body `title`, `content`. Creates a note (201). 422 on invalid input. |
| GET | `/notes/<id>` | yes | Returns one of your notes. 404 if it doesn't exist or isn't yours. |
| PATCH | `/notes/<id>` | yes | Update `title` and/or `content`. 404 if not yours, 422 on invalid input. |
| DELETE | `/notes/<id>` | yes | Deletes your note (204). 404 if not yours. |

Other users' notes return **404** (not 403) so their existence isn't revealed.
