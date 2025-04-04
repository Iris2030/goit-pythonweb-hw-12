from datetime import datetime, timedelta

contact_data = {
        "first_name": "Mia",
        "last_name": "Lee",
        "email": "mialee@example.com",
        "phone": "0973887897",
        "birth_date": "1987-12-06"
    }


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Mia"
    assert data["last_name"] == "Lee"
    assert data["email"] == "mialee@example.com"
    assert "id" in data

def test_create_contact_email_exists(client, get_token):
    client.post("/api/contacts", json=contact_data, headers={"Authorization": f"Bearer {get_token}"})

    contact_data_with_existing_email = {
        **contact_data,
        "email": "mial@example.com",
    }
    response = client.post(
        "/api/contacts",
        json=contact_data_with_existing_email,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Contact with email=mialee@example.com already exists"


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Mia"
    assert data["last_name"] == "Lee"
    assert data["email"] == "mial@example.com"
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/100", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]

def test_update_contact(client, get_token):
    contact_update_data = {
        "first_name": "Mia Updated",
        "email": "mianew@example.com",
        "phone": "976665432",
        "birth_date": "1988-04-19"
    }
    response = client.patch(
        "/api/contacts/1",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Mia Updated"
    assert data["email"] == "mianew@example.com"
    assert "id" in data

def test_update_contact_not_found(client, get_token):
    contact_update_data = {
        "first_name": "Somebody",
        "email": "somebody@example.com",
        "phone": "979999999",
        "birth_date": "1989-11-22"
    }
    response = client.patch(
        "/api/contacts/100",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact_email_exists(client, get_token):
    client.post("/api/contacts", json=contact_data, headers={"Authorization": f"Bearer {get_token}"})
    contact_data_to_update = {"email": "mial@example.com"}
    response = client.patch(
        "/api/contacts/2",
        json=contact_data_to_update,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Contact with email=mial@example.com already exists"




def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Mia Updated"
    assert "id" in data

def test_delete_contact_not_found(client, get_token):
    response = client.delete(
        "/api/contacts/100", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_upcoming_birthdays(client, get_token):
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    contact = {**contact_data, "birth_date":tomorrow_str, "email":"birth@gmail.com"}
    res = client.post("/api/contacts", json=contact, headers={"Authorization": f"Bearer {get_token}"})
    print(res.json())

    response = client.get("/api/contacts/upcoming-birthdays", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "birth_date" in data[0]