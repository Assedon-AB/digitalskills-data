""" Upploads finished data via API """
import requests
import os
import json

def upload_data(data, collection="kompetenser" ):
    API_URL = os.environ.get("API_URL")
    if not API_URL:
        API_URL = "http://localhost:8080/api/v1/"

    ORIGIN = os.environ.get("ORIGIN")
    if not ORIGIN:
        API_URL = "http://localhost:3000"

    API_KEY = os.environ.get("API_KEY")

    headers = {
        "x-api-key": API_KEY,
        "Origin": ORIGIN,
        "Content-Type": "application/json"
    }

    if(collection == "bransch"):
        body = data
        r = requests.post(API_URL+collection, json.dumps(body), headers=headers)
        print(r.status_code)
        if r.status_code != 201:
            print(r.text)
    else:
        for d in data:
            if(d):
                body = data[d]
                body["name"] = d

                r = requests.post(API_URL+collection, json.dumps(body), headers=headers)
                print(r.status_code)
                if r.status_code != 201:
                    print(r.text)

if __name__ == "__main__":
    data = {}
    with open("./data/skills_data_complete.json", "r") as fd:
        data = json.load(fd)

    print(len(list(data)))
    keysToRemove = []

    for key in list(data):
        if "ad_series" in data[key] and data[key]["ad_series"] and data[key]["ad_series"]["values"]:
            series_length = len(data[key]["ad_series"]["values"])

            data[key]["num"] = data[key]["ad_series"]["values"][series_length - 1]

            # Checking if enough data to be passing treshold
            if series_length < 6:
                if sum(data[key]["ad_series"]["values"]) < 20:
                    keysToRemove.append(key)
                    del data[key]
                else:
                    print("DONT REMOVE: ",sum(data[key]["ad_series"]["values"]))
            else:
                if sum(data[key]["ad_series"]["values"][(series_length-5):]) < 20:
                    keysToRemove.append(key)
                    del data[key]
                else:
                    print("DONT REMOVE: ",sum(data[key]["ad_series"]["values"][(series_length-5):]))
        else:
            keysToRemove.append(key)
            del data[key]

    upload_data(data)

