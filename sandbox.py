import requests
import json

headers = {
    "x-api-key": "g8p5dw0glrb6yvk4rdpe9eaqb3unwr",
    "Content-Type": "application/json",
    "Origin": "http://localhost:3000"
}

r = requests.get("http://localhost:8080/api/v1/yrken", headers=headers)
data = r.json()

for skill in data:
    name = skill["name"]
    docId = skill["_id"]
    num = None

    if skill["ad_series"]["values"] and len(skill["ad_series"]["values"]) > 0:
        num = skill["ad_series"]["values"][len(skill["ad_series"]["values"]) - 1]

    ur = requests.put("http://localhost:8080/api/v1/yrken/" + docId, json.dumps({"num": num, "name": name}), headers=headers)
    print(ur.status_code)
