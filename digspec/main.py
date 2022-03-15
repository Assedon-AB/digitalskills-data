import json
from extract_ad_info import extract_ad_info
from extract_skills import extract_skills
from enrich_ads import enrich_ads
from relationship_builder import create_relationships
from prediction_builder import create_predictions
from upload_data import upload_data
from get_industry_data import get_industry_data
from database_id_populator import populate_ids

def main(use_enrichment=False):
    # Filtrera annonser.
    ads = []
    try:
        with open("ads/all_ads.json") as fp:
            ads = json.load(fp)
    except:
        print("No all ads file found")

    if len(ads) == 0:
        all_ads = extract_ad_info()
        for ad_list in all_ads:
            ads.extend(ad_list)

        with open("ads/all_ads.json", "w") as fp:
            json.dump(ads, fp)

    skills = {}
    jobs = {}
    if(not use_enrichment):
        skills = extract_skills(ads)
        jobs = enrich_ads(ads)
    else:
        skills, jobs = enrich_ads(ads, enrich_skills=True)

    # Skapa relationer mellan kompetenser, yrke och mjukvärden. ifall enrichment inte användes för skills
    skills_data = {}
    jobs_data = {}
    if (not use_enrichment):
        skills_data, jobs_data = create_relationships(skills, jobs)
    else:
        skills_data = skills
        jobs_data =  jobs

    final_skills_data = {}
    final_jobs_data = {}
    # Skapa en prognos av yrken och kompetenser
    for skill in skills_data.keys():
        try:
            final_skills_data[skill] = skills_data[skill].copy()
            skills_pred_data = create_predictions(skills_data[skill]["series"])
            skills_pred_data.pop("eval_forecast")
            skills_pred_data.pop("backtest")
            final_skills_data[skill].update(skills_pred_data)
        except Exception as err:
            print(err)

    for occupation in jobs_data.keys():
        try:
            final_jobs_data[occupation] = jobs_data[occupation].copy()
            occupations_pred_data = create_predictions(jobs_data[occupation]["series"])
            occupations_pred_data.pop("eval_forecast")
            occupations_pred_data.pop("backtest")
            final_jobs_data[occupation].update(occupations_pred_data)
        except Exception as err:
            print(err)

    industry_data = get_industry_data(ads)
    industry_data = create_predictions(industry_data["series"])
    industry_data.pop("series")
    industry_data.pop("eval_forecast")
    industry_data.pop("backtest")

    industry_data["num"] = industry_data["ad_series"]["values"][len(industry_data["ad_series"]["values"]) - 1]

    # Rensar bort den gamla tidsserien ur datan.
    for key in final_jobs_data.keys():
        final_jobs_data[key].pop("series")
        try:
            if "ad_series" in final_jobs_data[key] and final_jobs_data[key]["ad_series"] and final_jobs_data[key]["ad_series"]["values"]:
                final_jobs_data[key]["num"] = final_jobs_data[key]["ad_series"]["values"][len(final_jobs_data[key]["ad_series"]["values"]) - 1]
        except Exception as err:
            print(err)

    for skillKey in final_skills_data.keys():
        final_skills_data[skillKey].pop("series")
        try:
            if "ad_series" in final_skills_data[key] and final_skills_data[skillKey]["ad_series"] and final_skills_data[key]["ad_series"]["values"]:
                final_skills_data[skillKey]["num"] = skill["ad_series"]["values"][len(skill["ad_series"]["values"]) - 1]
        except Exception as err:
            print(err)

    with open("data/skills_data_complete.json", "w") as fd:
        json.dump(final_skills_data, fd)

    with open("data/occupations_data_complete.json", "w") as fd:
        json.dump(final_jobs_data, fd)

    # Laddar upp data
    upload_data(final_skills_data)
    upload_data(final_jobs_data, "yrken")
    upload_data(industry_data, "bransch")

    # Lägger till idn till kompetenser och yrken under relaterade komptenser samt yrken.
    populate_ids()

if __name__ == "__main__":
    main(use_enrichment=True)
