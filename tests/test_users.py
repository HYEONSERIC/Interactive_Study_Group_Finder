from fastapi.testclient import TestClient
from study_buddy_api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Study Buddy API is running"}

#def test_login_success():
 #   response = client.post("/users", json={
  #      "name": "TESTBOIBRAH1",
   #     "email": "TESTBOIBRAH1@example.com",
    #    "password": "password123BRAH1"
    #})
    #assert response.status_code == 200

def test_login_success():
    response = client.post("/login", json={
        "email": "test1@test1.com",
        "password": "test1"
    })
    assert response.status_code == 200
