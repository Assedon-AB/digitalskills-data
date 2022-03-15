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

SKILL_TO_ID = {}
OCCUPATION_TO_ID = {}

def populate_ids():
    print("> POPULATING IDS")
    skill_request = requests.get("http://localhost:8080/api/v1/kompetenser", headers=headers)
    skills = skill_request.json()

    for skill in skills:
        SKILL_TO_ID[skill["name"].lower()] = skill["_id"]

    occupation_request = requests.get("http://localhost:8080/api/v1/yrken", headers=headers)
    occupations = occupation_request.json()

    for occupation in occupations:
        OCCUPATION_TO_ID[occupation["name"].lower()] = occupation["_id"]

    print("> POPULATING SKILL IDS")
    for skill_id in SKILL_TO_ID.values():
        r = requests.get("http://localhost:8080/api/v1/kompetenser/"+skill_id, headers=headers)
        tmp_skill = r.json()

        if "jobs" in tmp_skill:
            tmp_jobs = tmp_skill["jobs"].copy()
            for job_name in tmp_jobs.keys():
                job_name_cleaned = job_name.split("__")[0].lower()
                if job_name_cleaned in OCCUPATION_TO_ID:
                    tmp_skill["jobs"][job_name_cleaned+"__"+OCCUPATION_TO_ID[job_name_cleaned]] = tmp_skill["jobs"][job_name]
                    if job_name != job_name_cleaned+"__"+OCCUPATION_TO_ID[job_name_cleaned]:
                        del tmp_skill["jobs"][job_name]
                else:
                    tmp_skill["jobs"][job_name_cleaned+"__noId"] = tmp_skill["jobs"][job_name]
                    if job_name != job_name_cleaned+ "__noId":
                        del tmp_skill["jobs"][job_name]

        if "skills" in tmp_skill:
            tmp_skills = tmp_skill["skills"].copy()
            for skill_name in tmp_skills.keys():
                skill_name_cleaned = skill_name.split("__")[0].lower()
                if skill_name_cleaned in SKILL_TO_ID:
                    tmp_skill["skills"][skill_name_cleaned+"__"+SKILL_TO_ID[skill_name_cleaned]] = tmp_skill["skills"][skill_name]
                    if skill_name != skill_name_cleaned+"__"+SKILL_TO_ID[skill_name_cleaned]:
                        del tmp_skill["skills"][skill_name]
                else:
                    tmp_skill["skills"][skill_name_cleaned+"__noId"] = tmp_skill["skills"][skill_name]
                    if skill_name != skill_name_cleaned + "__noId":
                        del tmp_skill["skills"][skill_name]

        update_request = requests.put("http://localhost:8080/api/v1/kompetenser/"+skill_id, data=json.dumps(tmp_skill), headers=headers)

    print("> POPULATING OCCUPATION IDS")
    for occupation_id in OCCUPATION_TO_ID.values():
        r = requests.get("http://localhost:8080/api/v1/yrken/"+occupation_id, headers=headers)
        tmp_job = r.json()

        if "jobs" in tmp_job:
            tmp_jobs = tmp_job["jobs"].copy()
            for job_name in tmp_jobs.keys():
                job_name_cleaned = job_name.split("__")[0].lower()
                if job_name_cleaned in OCCUPATION_TO_ID:
                    tmp_job["jobs"][job_name_cleaned+"__"+OCCUPATION_TO_ID[job_name_cleaned]] = tmp_job["jobs"][job_name]
                    if job_name != job_name_cleaned+"__"+OCCUPATION_TO_ID[job_name_cleaned]:
                        del tmp_job["jobs"][job_name]
                else:
                    tmp_job["jobs"][job_name_cleaned+"__noId"] = tmp_job["jobs"][job_name]
                    if job_name != job_name_cleaned+ "__noId":
                        del tmp_job["jobs"][job_name]

        if "skills" in tmp_job:
            tmp_skills = tmp_job["skills"].copy()
            for skill_name in tmp_skills.keys():
                skill_name_cleaned = skill_name.split("__")[0].lower()
                if skill_name_cleaned in SKILL_TO_ID:
                    tmp_job["skills"][skill_name_cleaned+"__"+SKILL_TO_ID[skill_name_cleaned]] = tmp_job["skills"][skill_name]
                    if skill_name != skill_name_cleaned+"__"+SKILL_TO_ID[skill_name_cleaned]:
                        del tmp_job["skills"][skill_name]
                else:
                    tmp_job["skills"][skill_name_cleaned+"__noId"] = tmp_job["skills"][skill_name]
                    if skill_name != skill_name_cleaned + "__noId":
                        del tmp_job["skills"][skill_name]

        update_request = requests.put("http://localhost:8080/api/v1/yrken/"+occupation_id, data=json.dumps(tmp_job), headers=headers)

if __name__ == "__main__":
    populate_ids()
