""" Creates relationship between skills, traits, and jobs. """
import json
import operator

def create_relationships(skills_data, jobs_data):
    jobs =  {}
    skills = {}
    for job in jobs_data.keys():
        try:
            for adId in jobs_data[job]["adIds"]:
                for skill in skills_data.keys():
                    if adId in skills_data[skill]["adIds"]:
                        if job not in jobs:
                            jobs[job] = {
                                "skills":  {},
                                "traits": jobs_data[job]["traits"],
                                "geos": jobs_data[job]["geos"]
                            }

                        if skill not in jobs[job]["skills"]:
                            jobs[job]["skills"][skill] = 1

                        if skill not in skills:
                            skills[skill] = {
                                "jobs": {},
                                "geos": {}
                            }

                        if job not in skills[skill]["jobs"]:
                            skills[skill]["jobs"][job] = 1

                        top_10_geos = sorted(jobs_data[job]["geos"].items(), key=operator.itemgetter(1), reverse=True)[:10]
                        for location in top_10_geos:
                            if location[0] not in skills[skill]["geos"]:
                                skills[skill]["geos"][location[0]] = location[1]
                            else:
                                skills[skill]["geos"][location[0]] += location[1]

                        jobs[job]["skills"][skill] += 1
                        skills[skill]["jobs"][job] += 1
        except Exception as err:
            pass

    with open("data/job-relationship.json", "w") as fd:
        json.dump(jobs, fd)

    with open("data/skill-relationship.json", "w") as fd:
        json.dump(skills, fd)

    return skills, jobs

if __name__ == "__main__":
    skills_data = {}
    with open("data/skills_data.json", "r") as fd:
        skills_data = json.load(fd)

    jobs_data = {}
    with open("enriched/2020-enriched-jobs.json", "r") as fd:
        jobs_data = json.load(fd)

    create_relationships(skills_data, jobs_data)
