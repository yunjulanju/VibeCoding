import os

# app 모듈 임포트(=설정/엔진 생성) 전에 테스트용 환경을 지정한다.
os.environ["DATABASE_URL"] = "sqlite:///./test_authdb.sqlite3"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def signup_user(client, email="player@example.com", username="player1", password="password123"):
    return client.post(
        "/auth/signup",
        json={"email": email, "username": username, "password": password},
    )


def login_user(client, email="player@example.com", password="password123"):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
