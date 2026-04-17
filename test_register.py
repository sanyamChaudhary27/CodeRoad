import requests

# Test registration
response = requests.post(
    "https://coderoad-gmq6.onrender.com/api/v1/auth/register",
    json={
        "username": "testuser123",
        "email": "test@example.com",
        "password": "TestPass123"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
