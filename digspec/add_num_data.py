import requests
import os
import json

API_URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")
headers = {
    "x-api-key": API_KEY,
    "Origin": "http://localhost:3000",
    "Content-Type": "application/json"
}

def add_num_data():
    skill_request = requests.get("http://localhost:8080/api/v1/kompetenser", headers=headers)
    skills = skill_request.json()

    for skill in skills:
        try:
            tmp_skill = {
                "name": skill["name"],
                "num": 0
            }

            if "ad_series" in skill and skill["ad_series"] and skill["ad_series"]["values"]:
                tmp_skill["num"] = skill["ad_series"]["values"][len(skill["ad_series"]["values"]) - 1]

            update_request = requests.put("http://localhost:8080/api/v1/kompetenser/"+skill["_id"], data=json.dumps(tmp_skill), headers=headers)
        except Exception as err:
            print(err)


if __name__ == "__main__":
    add_num_data()
