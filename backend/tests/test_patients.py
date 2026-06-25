def test_create_patient(client, test_user):
    """Test creating a new patient."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    patient_data = {
        "patient_id": "PAT001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "phone": "555-1234",
        "email": "john.doe@example.com",
        "address": "123 Main St"
    }
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == "PAT001"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data


def test_create_duplicate_patient(client, test_user):
    """Test creating patient with duplicate patient_id."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    patient_data = {
        "patient_id": "PAT002",
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1985-05-20",
        "gender": "female"
    }
    # Create first patient
    client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # Try to create duplicate
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 400


def test_get_patient_by_id(client, test_user):
    """Test getting patient by ID."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    patient_data = {
        "patient_id": "PAT003",
        "first_name": "Bob",
        "last_name": "Johnson",
        "date_of_birth": "1975-08-10",
        "gender": "male"
    }
    create_response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    patient_id = create_response.json()["id"]
    
    # Get patient
    response = client.get(f"/api/v1/patients/{patient_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["first_name"] == "Bob"


def test_get_patient_not_found(client, test_user):
    """Test getting non-existent patient."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/api/v1/patients/99999", headers=headers)
    assert response.status_code == 404


def test_get_patient_by_external_id(client, test_user):
    """Test getting patient by external patient_id."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    patient_data = {
        "patient_id": "PAT004",
        "first_name": "Alice",
        "last_name": "Williams",
        "date_of_birth": "1988-03-25",
        "gender": "female"
    }
    client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # Get by external ID
    response = client.get("/api/v1/patients/external/PAT004", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "PAT004"


def test_update_patient(client, test_user):
    """Test updating patient information."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    patient_data = {
        "patient_id": "PAT005",
        "first_name": "Charlie",
        "last_name": "Brown",
        "date_of_birth": "1992-11-30",
        "gender": "male",
        "phone": "555-0000"
    }
    create_response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    patient_id = create_response.json()["id"]
    
    # Update patient
    update_data = {
        "phone": "555-9999",
        "email": "charlie.brown@example.com"
    }
    response = client.put(f"/api/v1/patients/{patient_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "555-9999"
    assert data["email"] == "charlie.brown@example.com"


def test_update_patient_not_found(client, test_user):
    """Test updating non-existent patient."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    update_data = {"phone": "555-9999"}
    response = client.put("/api/v1/patients/99999", json=update_data, headers=headers)
    assert response.status_code == 404


def test_list_patients(client, test_user):
    """Test listing all patients."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create multiple patients
    for i in range(3):
        patient_data = {
            "patient_id": f"PAT010{i}",
            "first_name": f"Patient{i}",
            "last_name": f"Test{i}",
            "date_of_birth": "1990-01-01",
            "gender": "male"
        }
        client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # List patients
    response = client.get("/api/v1/patients/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_list_patients_pagination(client, test_user):
    """Test patient list pagination."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create patients
    for i in range(5):
        patient_data = {
            "patient_id": f"PAT020{i}",
            "first_name": f"Page{i}",
            "last_name": f"Test{i}",
            "date_of_birth": "1990-01-01",
            "gender": "female"
        }
        client.post("/api/v1/patients/", json=patient_data, headers=headers)
    
    # Get first page
    response = client.get("/api/v1/patients/?skip=0&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
