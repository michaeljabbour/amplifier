import requests
import time

def test_contact_manager_api():
    # Give the server a brief moment to ensure it's running (if needed)
    time.sleep(1)

    # 1. Test adding a new contact via POST
    new_contact = {"name": "Alice", "phone": "123456"}
    resp = requests.post("http://localhost:5000/contacts", json=new_contact)
    assert resp.status_code in (200, 201), f"POST /contacts returned {resp.status_code}, expected 200 or 201."
    data = resp.json()
    # Verify the returned JSON contains the correct data and an id
    assert data.get("name") == "Alice" and data.get("phone") == "123456", "POST /contacts response JSON data mismatch."
    assert "id" in data, "POST /contacts response missing 'id' field."
    contact_id = data["id"]

    # 2. Test retrieving contacts via GET
    resp2 = requests.get("http://localhost:5000/contacts")
    assert resp2.status_code == 200, f"GET /contacts returned {resp2.status_code}, expected 200."
    contacts_list = resp2.json()
    assert isinstance(contacts_list, list), "GET /contacts did not return a JSON list."
    # There should be at least one contact and the one we added should be present
    matching_contacts = [c for c in contacts_list if c.get("id") == contact_id]
    assert matching_contacts, "Added contact not found in GET /contacts list."
    found = matching_contacts[0]
    assert found.get("name") == "Alice" and found.get("phone") == "123456", "Contact data in list does not match expected values."