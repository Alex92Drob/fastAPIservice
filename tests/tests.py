from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@localhost:5452/test?sslmode=disable"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register():
    response = client.post("/register", json={
        "email": "test@example.com",
        "username": "test",
        "password": "testpassword",
        "first_name": "Bob",
        "last_name": "Test",
        "balance": 100
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_login():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "You are now logged in"


def test_logout():
    response = client.post("/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "User logged out successfully"


def test_change_password():
    response = client.post("/change_password", json={
        "email": "test@example.com",
        "password": "testpassword",
        "new_password": "newpassword",
        "confirm_new_password": "newpassword"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"


def test_get_users():
    response = client.get("/get_users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["id"] is not None
    assert users[0]["email"] == "test@example.com"
    assert users[0]["first_name"] == "Bob"
    assert users[0]["last_name"] == "Test"
    assert users[0]["created_at"] is not None
    assert users[0]["last_activity_at"] is not None
    assert users[0]["updated_at"] is not None


def test_get_balance():
    response = client.get("/balance?first_name=Bob&last_name=Test")
    assert response.status_code == 200
    assert response.json()["balance"] == 100


def test_withdraw_balance():
    response = client.put("/withdraw_balance?first_name=Bob&last_name=Test&amount=30")
    assert response.status_code == 200
    assert response.json() == {"message": "Balance updated", "new_balance": 70}


def test_get_profile():
    response = client.get("/profile?first_name=Bob&last_name=Test")
    assert response.status_code == 200
    assert response.json()["first_name"] == "Bob"
    assert response.json()["last_name"] == "Test"


def test_update_profile():
    response = client.put(
        "/update_profile",
        json={
            "email": "test@example.com",
            "username": "test",
            "first_name": "Bob",
            "last_name": "Test",
            "new_first_name": "Robert",
            "new_last_name": "Tester"
        }
    )
    assert response.status_code == 200