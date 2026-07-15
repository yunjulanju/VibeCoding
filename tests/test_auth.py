from tests.conftest import login_user, signup_user


def test_signup_success(client):
    resp = signup_user(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "player@example.com"
    assert body["username"] == "player1"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_duplicate_email(client):
    signup_user(client)
    resp = signup_user(client, username="player2")  # 같은 이메일, 다른 아이디
    assert resp.status_code == 409


def test_signup_duplicate_username(client):
    signup_user(client)
    resp = signup_user(client, email="other@example.com")  # 다른 이메일, 같은 아이디
    assert resp.status_code == 409


def test_signup_invalid_email(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "not-an-email", "username": "player1", "password": "password123"},
    )
    assert resp.status_code == 422


def test_signup_short_password(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "player@example.com", "username": "player1", "password": "short"},
    )
    assert resp.status_code == 422


def test_login_success(client):
    signup_user(client)
    resp = login_user(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    signup_user(client)
    resp = login_user(client, password="wrongpassword")
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = login_user(client, email="ghost@example.com")
    assert resp.status_code == 401
