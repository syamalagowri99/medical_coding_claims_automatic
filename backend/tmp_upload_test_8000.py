import os
import requests
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import create_user
from app.schemas.user import UserCreate

os.chdir(os.path.dirname(__file__))

# Ensure test user exists
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

base = 'http://127.0.0.1:8000/api/v1'

# Login
login_resp = requests.post(f'{base}/auth/login', data={'username':'apitestuser','password':'Password123!'}, timeout=10)
print('login status', login_resp.status_code)
print(login_resp.json())
login_resp.raise_for_status()
access_token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}

# Prepare file
file_path = os.path.join(os.path.dirname(__file__), 'tmp_test_upload.txt')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write('This is a test document for upload.\nPatient data and medical notes.\n')

with open(file_path, 'rb') as f:
    files = {'file': ('tmp_test_upload.txt', f, 'text/plain')}
    data = {'patient_id': '1', 'document_type': 'clinical_note'}
    upload_resp = requests.post(f'{base}/documents/upload', headers=headers, files=files, data=data, timeout=30)
    print('upload status', upload_resp.status_code)
    try:
        print(upload_resp.json())
    except Exception:
        print(upload_resp.text)

# List patient documents
list_resp = requests.get(f'{base}/documents/patient/1', headers=headers, timeout=10)
print('list status', list_resp.status_code)
try:
    print(list_resp.json())
except Exception:
    print(list_resp.text)
