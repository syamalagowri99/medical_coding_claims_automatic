def test_register_user(client):
    """Test user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "coder"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "coder"
    assert "id" in data


def test_register_duplicate_user(client):
    """Test registration with duplicate username."""
    user_data = {
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "password123",
        "role": "coder"
    }
    # Register first user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register duplicate
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400


def test_login_success(client):
    """Test successful login."""
    # Register user first
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass123",
        "role": "admin"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "loginpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_get_current_user(client, test_user):
    """Test getting current user info."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_user_by_id_admin(client, test_user):
    """Test admin getting user by ID."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get(f"/api/v1/auth/users/{test_user['user']['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user['user']['id']


def test_get_user_by_id_non_admin(client):
    """Test non-admin trying to get user by ID."""
    # Create non-admin user
    user_data = {
        "username": "regularuser",
        "email": "regular@example.com",
        "password": "regularpass123",
        "role": "coder"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    user_id = response.json()["id"]
    
    # Login as non-admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "regularuser", "password": "regularpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Try to get another user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/auth/users/{user_id}", headers=headers)
    assert response.status_code == 403
