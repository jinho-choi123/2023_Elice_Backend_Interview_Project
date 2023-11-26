from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_hc():
    response = client.get("/hc")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Server is Running!"
    }