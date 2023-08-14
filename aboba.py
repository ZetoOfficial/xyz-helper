import json

import requests

url = "http://localhost:8090/api/export"

payload = json.dumps({"session_id": "iBLRLtBzajYxT3uBkyQy", "optimal_clusters": 12, "cluster_indexes": [0]})
headers = {'Content-Type': 'application/json'}

with requests.request("POST", url, headers=headers, data=payload) as r:
    for chunk in r.iter_content(1024):
        print(chunk)
