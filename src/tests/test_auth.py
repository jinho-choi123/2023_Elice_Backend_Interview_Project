from fastapi.testclient import TestClient
from fastapi import status
from src.types.authTypes import authSigninRequest, authSignupRequest, authResponse

from main import app

client = TestClient(app)

# signin without cookie
def test_signin1():
    signinForm = authSigninRequest(
        email = "testing",
        password = "testing"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())
    print(response)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == authResponse(success=False, message = "Invalid email or password.").model_dump()