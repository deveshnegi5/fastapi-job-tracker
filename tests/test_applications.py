def test_create_application(client, auth_headers):
    response = client.post(
        "/applications",
        json={"company": "Google", "role": "Backend Developer"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Google"
    assert data["status"] == "applied"


def test_create_application_requires_auth(client):
    response = client.post("/applications", json={"company": "Google", "role": "Backend Developer"})
    assert response.status_code == 401


def test_list_applications_empty(client, auth_headers):
    response = client.get("/applications", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_applications_after_create(client, auth_headers):
    client.post("/applications", json={"company": "Google", "role": "Backend Developer"}, headers=auth_headers)
    client.post("/applications", json={"company": "Amazon", "role": "SDE"}, headers=auth_headers)

    response = client.get("/applications", headers=auth_headers)
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_update_application(client, auth_headers):
    create = client.post("/applications", json={"company": "Google", "role": "Backend Developer"}, headers=auth_headers)
    app_id = create.json()["id"]

    response = client.put(
        f"/applications/{app_id}",
        json={"company": "Google", "role": "Backend Developer", "status": "interview"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "interview"


def test_delete_application(client, auth_headers):
    create = client.post("/applications", json={"company": "Google", "role": "Backend Developer"}, headers=auth_headers)
    app_id = create.json()["id"]

    response = client.delete(f"/applications/{app_id}", headers=auth_headers)
    assert response.status_code == 200

    get_response = client.get(f"/applications/{app_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_user_cannot_see_others_applications(client):
    client.post("/register", json={"email": "a@test.com", "password": "pass123"})
    login_a = client.post("/login", data={"username": "a@test.com", "password": "pass123"})
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

    client.post("/register", json={"email": "b@test.com", "password": "pass123"})
    login_b = client.post("/login", data={"username": "b@test.com", "password": "pass123"})
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    client.post("/applications", json={"company": "Google", "role": "Backend Developer"}, headers=headers_a)

    response = client.get("/applications", headers=headers_b)
    assert response.json()["total"] == 0   # user B sees nothing, confirms isolation from Step 4