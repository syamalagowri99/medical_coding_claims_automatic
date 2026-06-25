import requests
import json

r = requests.get('http://127.0.0.1:8000/api/v1/openapi.json', timeout=5)
r.raise_for_status()
j = r.json()
ref = j['paths']['/api/v1/documents/upload']['post']['requestBody']['content']['multipart/form-data']['schema']['$ref']
name = ref.split('/')[-1]
print(ref)
print(json.dumps(j['components']['schemas'][name], indent=2))
