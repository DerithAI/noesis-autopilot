```python
import pytest
from main import app, User, TokenData

def test_login():
    user = User(username="admin", password="password")
    response = app.test_client.post("/token", json=user.dict())
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "admin"

def test_read_users_me():
    client = app.test_client()
    token = {"access_token": "test_token", "token_type": "bearer"}
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "admin"
```