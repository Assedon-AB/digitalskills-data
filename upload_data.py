""" Upploads finished data via API """
import requests
import os

def upload_data(data, collection="kompetenser" ):
    API_URL = os.environ.get("API_URL")
    if not API_URL:
        API_URL = "http://localhost:8080/api/v1/"

    for d in data:
        r = requests.post(API_URL+collection, d)

if __name__ == "__main__":
    data = []
    upload_data(data)
