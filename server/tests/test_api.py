from tests.conftest import auth, register


def test_signup_login_me(client):
    r = client.post("/signup", json={"username": "ann", "password": "secret123", "password_confirmation": "secret123"})
    assert r.status_code == 201
    assert r.get_json()["user"]["username"] == "ann"

    r = client.post("/login", json={"username": "ann", "password": "secret123"})
    assert r.status_code == 200
    token = r.get_json()["token"]

    r = client.get("/me", headers=auth(token))
    assert r.status_code == 200 and r.get_json()["username"] == "ann"


def test_signup_validation_and_duplicates(client):
    bad = client.post("/signup", json={"username": "ann", "password": "secret123", "password_confirmation": "nope"})
    assert bad.status_code == 422 and bad.get_json()["errors"]
    register(client, "ann")
    dup = client.post("/signup", json={"username": "Ann", "password": "secret123", "password_confirmation": "secret123"})
    assert dup.status_code == 422


def test_login_wrong_password(client):
    register(client, "ann")
    r = client.post("/login", json={"username": "ann", "password": "wrong"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers=auth("garbage")).status_code == 401


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401
    assert client.post("/notes", json={"title": "x", "content": "y"}).status_code == 401


def test_crud_flow(client):
    h = auth(register(client, "ann"))
    r = client.post("/notes", json={"title": "Hi", "content": "there"}, headers=h)
    assert r.status_code == 201
    nid = r.get_json()["id"]

    assert client.get(f"/notes/{nid}", headers=h).status_code == 200
    r = client.patch(f"/notes/{nid}", json={"title": "Changed"}, headers=h)
    assert r.status_code == 200 and r.get_json()["title"] == "Changed"
    assert client.patch(f"/notes/{nid}", json={}, headers=h).status_code == 422
    assert client.post("/notes", json={"title": "only"}, headers=h).status_code == 422
    assert client.delete(f"/notes/{nid}", headers=h).status_code == 204
    assert client.get(f"/notes/{nid}", headers=h).status_code == 404


def test_pagination(client):
    h = auth(register(client, "ann"))
    for i in range(25):
        client.post("/notes", json={"title": f"n{i}", "content": "c"}, headers=h)
    body = client.get("/notes?page=3&per_page=10", headers=h).get_json()
    assert len(body["notes"]) == 5
    assert body["total"] == 25 and body["pages"] == 3 and not body["has_next"]
    assert client.get("/notes?page=0", headers=h).status_code == 400


def test_users_cannot_touch_each_others_notes(client):
    ann, bob = auth(register(client, "ann")), auth(register(client, "bob"))
    nid = client.post("/notes", json={"title": "secret", "content": "c"}, headers=ann).get_json()["id"]

    assert client.get("/notes", headers=bob).get_json()["total"] == 0
    assert client.get(f"/notes/{nid}", headers=bob).status_code == 404
    assert client.patch(f"/notes/{nid}", json={"title": "pwn"}, headers=bob).status_code == 404
    assert client.delete(f"/notes/{nid}", headers=bob).status_code == 404
    assert client.get(f"/notes/{nid}", headers=ann).get_json()["title"] == "secret"
