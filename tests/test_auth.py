def test_register_user(client):
    response = client.post("/register", json={"email": "a@test.com", "password": "pass123"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "a@test.com"
    assert "id" in data


def test_register_duplicate_email(client):
    client.post("/register", json={"email": "a@test.com", "password": "pass123"})
    response = client.post("/register", json={"email": "a@test.com", "password": "different"})
    assert response.status_code == 400


def test_login_success(client):
    client.post("/register", json={"email": "a@test.com", "password": "pass123"})
    response = client.post("/login", data={"username": "a@test.com", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/register", json={"email": "a@test.com", "password": "pass123"})
    response = client.post("/login", data={"username": "a@test.com", "password": "wrong"})
    assert response.status_code == 401