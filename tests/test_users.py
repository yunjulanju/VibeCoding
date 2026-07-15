from tests.conftest import auth_header, login_user, signup_user


def _register_and_token(client) -> str:
    signup_user(client)
    return login_user(client).json()["access_token"]


def test_read_me_success(client):
    token = _register_and_token(client)
    resp = client.get("/users/me", headers=auth_header(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "player@example.com"
    assert body["username"] == "player1"


def test_read_me_no_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_read_me_invalid_token(client):
    resp = client.get("/users/me", headers=auth_header("garbage.token.value"))
    assert resp.status_code == 401


def test_delete_me_success(client):
    token = _register_and_token(client)
    resp = client.delete("/users/me", headers=auth_header(token))
    assert resp.status_code == 204


def test_deleted_user_cannot_login(client):
    token = _register_and_token(client)
    client.delete("/users/me", headers=auth_header(token))
    resp = login_user(client)
    assert resp.status_code == 401


def test_deleted_user_token_rejected(client):
    token = _register_and_token(client)
    client.delete("/users/me", headers=auth_header(token))
    resp = client.get("/users/me", headers=auth_header(token))
    assert resp.status_code == 401
