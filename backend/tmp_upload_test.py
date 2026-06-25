import os
import requests

BASE = "http://127.0.0.1:8000/api/v1"
USER = {
    "username": "uploadtester",
    "password": "Password123!",
}

session = requests.Session()
login = session.post(f"{BASE}/auth/login", data=USER)
print("login", login.status_code, login.text)
if login.status_code != 200:
    raise SystemExit("Login failed")

access_token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
file_path = os.path.expanduser(r"C:\Users\jgowri\Downloads\Dummy_Medical_Report_2.pdf")
print("file exists", os.path.exists(file_path), file_path)
with open(file_path, "rb") as f:
    response = session.post(
        f"{BASE}/documents/upload",
        params={"patient_id": 1, "document_type": "lab_result"},
        files={"file": ("Dummy_Medical_Report_2.pdf", f, "application/pdf")},
        headers=headers,
    )
print("upload", response.status_code, response.text)
