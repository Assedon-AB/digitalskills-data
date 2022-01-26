""" Upploads finished data via API """
import requests
import os

def upload_data(data, collection="kompetenser" ):
    API_URL = os.environ.get("API_URL")
    if not API_URL:
        API_URL = "http://localhost:8080/api/v1/"

    API_KEY = os.environ.get("API_KEY")

    for d in data:
        r = requests.post(API_URL+collection, d, headers={
                "x-api-key": API_KEY,
                }
            )
        print(r.status_code)

if __name__ == "__main__":
    data = [
            {
                "name": "React",
                "description": "react framework"
                }
            ]
    upload_data(data)
