import requests

# Test login with migrated user
response = requests.post(
    "https://coderoad-gmq6.onrender.com/api/v1/auth/login",
    json={
        "email": "reddyreedy777@gmail.com",
        "password": "TempPass123"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
