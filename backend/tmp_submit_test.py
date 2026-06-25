from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

r = client.post('/api/v1/auth/register', json={'username':'testuser2','password':'testpass2','email':'test2@example.com'})
print('register', r.status_code, r.text)

l = client.post('/api/v1/auth/login', data={'username':'testuser2','password':'testpass2'})
print('login', l.status_code, l.text)

if l.status_code == 200:
    token = l.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    r2 = client.post('/api/v1/claims/2/submit', headers=headers)
    print('submit', r2.status_code, r2.text)
    try:
        print('json', r2.json())
    except Exception as e:
        print('json err', e)
