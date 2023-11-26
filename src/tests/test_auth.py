import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi import status
from src.types.authTypes import authSigninRequest, authSignupRequest, authResponse

from main import app
from src.db.database import Base, get_db


# Get Test DB URL
TEST_DB_URL = os.environ["POSTGRES_TEST_DB_URL"]

engine = create_engine(TEST_DB_URL)

TEST_SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try: 
        db = TEST_SessionLocal()
        yield db 
    finally:
        db.close()

@pytest.fixture()
def refresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# signin invalid email and password
def test_signin_with_invalid_email_password(refresh_db):
    signinForm = authSigninRequest(
        email = "testing",
        password = "testing"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == authResponse(success=False, message = "User not found. Please signup.").model_dump()

# signup twice
def test_signup(refresh_db):
    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )

    response = client.post("/api/auth/signup", json=signupForm.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success = True, message = "signup success").model_dump()

    response = client.post("/api/auth/signup", json=signupForm.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success = False, message = "Signup Failed. Email is already in use.").model_dump()

# signup and signin
def test_signin(refresh_db):

    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )

    response = client.post("/api/auth/signup", json=signupForm.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success = True, message = "signup success").model_dump()

    signinForm = authSigninRequest(
        email = "mango@mango.mango",
        password = "simplepassword"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success=True, message = "signin success").model_dump()

def test_signin_with_invalid_password(refresh_db):
    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )

    response = client.post("/api/auth/signup", json=signupForm.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success = True, message = "signup success").model_dump()

    signinForm = authSigninRequest(
        email = "mango@mango.mango",
        password = "wrongpassword"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == authResponse(success=False, message = "Invalid email or password.").model_dump()

def test_signup_signin_signout(refresh_db):
    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )

    response = client.post("/api/auth/signup", json=signupForm.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success = True, message = "signup success").model_dump()

    signinForm = authSigninRequest(
        email = "mango@mango.mango",
        password = "simplepassword"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success=True, message = "signin success").model_dump()

    response = client.post("/api/auth/signout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == authResponse(success=True, message = "logout success").model_dump()

    # logout twice will cause error
    response = client.post("/api/auth/signout")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}
