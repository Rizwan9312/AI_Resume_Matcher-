"""Test registration endpoint."""
import urllib.request
import urllib.error
import json

data = json.dumps({
    "email": "test@test.com",
    "password": "testpassword123",
    "full_name": "Test User"
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/register",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Status: {resp.status}")
        print(f"Body: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
