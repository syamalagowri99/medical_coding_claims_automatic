import os, requests, json
endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
key = os.environ.get('AZURE_OPENAI_API_KEY')
api_version = os.environ.get('AZURE_OPENAI_API_VERSION','2024-02-01')
if not endpoint or not key:
    print('MISSING_ENV')
else:
    url = endpoint.rstrip('/') + '/openai/deployments?api-version=' + api_version
    headers = {'api-key': key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print('STATUS', r.status_code)
        try:
            print(json.dumps(r.json(), indent=2)[:2000])
        except Exception:
            print('RAW', r.text[:2000])
    except Exception as e:
        print('ERR', type(e).__name__, str(e))
