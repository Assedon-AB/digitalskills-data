""" Finds skills and saves as DateTime series """
import json
import pandas as pd
import numpy as np
import csv
import re

def get_ads_data():
    """ Gets ads data """
    years = ["2020", "2021"]#["2014","2015","2016","2017","2018","2019","2020","2021"] #["2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
    ads = []
    for year in years:
        ad = json.load(open(f"./ads/{year}.json", "r"))
        ads.extend(ad)
    return ads

def get_whitelist():
    """ Reads in whitelist """
    file = open("./whitelist.csv")
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row)
    file.close()
    return rows

def save_skills_data_to_json(skills_data):
    skills_data_json = skills_data.copy()
    for key in skills_data.keys():
        skills_data_json[key]["series"] = skills_data[key]["series"].to_json(indent=4)
        skills_data_json[key]["adIds"] = skills_data[key]["adIds"]

    with open(f"data/skills_data.json", "w", encoding="utf-8") as fd:
        json.dump(skills_data_json, fd, ensure_ascii=False, indent=4)


def extract_skills(ads):
    """ Goes through all skills in whitelist and extracts skill """
    whitelist = get_whitelist()

    num = 6087 # TODO: Change from hardcoded num -> dynamic value
    complete_date = pd.to_datetime("1st of January, 2006") + pd.to_timedelta(np.arange(num), 'D')
    index = pd.DatetimeIndex(complete_date)

    skills_data = {}
    for row in whitelist:
        skills_data[row[1]] = {"series": [], "adIds": [], "subgroup": row[2], "maingroup": row[3], "employers": {}}
        skills_data[row[1]]["series"] = pd.Series([0] * num, index=index)

    print(f"> Extracting skills from ads data")
    try:
        for adId, ad in enumerate(ads):
            if len(ad["date"]) > 9:
                date = ad["date"].split("T")[0].split(" ")[0]
                for row in whitelist:
                    skill_regex = row[0]

                    p = re.compile(skill_regex)
                    if bool(p.search(ad["doc_text"].lower())):
                        skills_data[row[1]]["series"][date] += 1
                        skills_data[row[1]]["adIds"].append(adId)

                        if "employer" in ad:
                            if ad["employer"] in skills_data[row[1]]["employers"]:
                                skills_data[row[1]]["employers"][ad["employer"]] += 1
                            else:
                                skills_data[row[1]]["employers"][ad["employer"]] = 1


        save_skills_data_to_json(skills_data)
    except Exception as err:
        print(err)
        save_skills_data_to_json(skills_data)

    return skills_data

if __name__ == "__main__":
    ads = get_ads_data()
    extract_skills(ads)
