import os
import requests
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import create_user
from app.schemas.user import UserCreate

# Ensure this script runs from the backend folder with the correct PYTHONPATH
os.chdir(os.path.dirname(__file__))

# Create a known test user if it does not exist
with SessionLocal() as db:
    existing = db.query(User).filter(User.username == 'apitestuser').first()
    if not existing:
        create_user(db, UserCreate(
            email='apitestuser@example.com',
            username='apitestuser',
            password='Password123!',
            full_name='API Test User',
            role='admin'
        ))

# Login to get access token
login_resp = requests.post(
    'http://127.0.0.1:8001/api/v1/auth/login',
    data={'username': 'apitestuser', 'password': 'Password123!'}
)
print('login status', login_resp.status_code)
print(login_resp.text)
login_resp.raise_for_status()
access_token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}

# Prepare a small text file for upload
file_path = os.path.join(os.path.dirname(__file__), 'tmp_test_upload.txt')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write('This is a test document for upload.\nPatient data and medical notes.\n')

with open(file_path, 'rb') as f:
    files = {'file': ('tmp_test_upload.txt', f, 'text/plain')}
    data = {'patient_id': '1', 'document_type': 'clinical_note'}
    upload_resp = requests.post(
        'http://127.0.0.1:8001/api/v1/documents/upload',
        headers=headers,
        files=files,
        data=data
    )
    print('upload status', upload_resp.status_code)
    print(upload_resp.text)

# List documents for patient 1
list_resp = requests.get(
    'http://127.0.0.1:8001/api/v1/documents/patient/1',
    headers=headers
)
print('list status', list_resp.status_code)
print(list_resp.text)
