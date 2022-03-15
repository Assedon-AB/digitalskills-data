""" Upploads finished data via API """
import requests
import os
import json

def upload_data(data, collection="kompetenser" ):
    API_URL = os.environ.get("API_URL")
    if not API_URL:
        API_URL = "http://localhost:8080/api/v1/"

    API_KEY = os.environ.get("API_KEY")

    if(collection == "bransch"):
        body = data
        r = requests.post(API_URL+collection, json.dumps(body), headers={
                "x-api-key": API_KEY,
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json"
                }
            )
        print(r.status_code)
    else:
        for d in data:
            if(d):
                body = data[d]
                body["name"] = d

                r = requests.post(API_URL+collection, json.dumps(body), headers={
                        "x-api-key": API_KEY,
                        "Origin": "http://localhost:3000",
                        "Content-Type": "application/json"
                        }
                    )
                print(r.status_code)

if __name__ == "__main__":
    data = {}
    with open("./data/skills_data_complete.json", "r") as fd:
        data = json.load(fd)

    upload_data(data)
