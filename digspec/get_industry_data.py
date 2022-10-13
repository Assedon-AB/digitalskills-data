import json
import pandas as pd
import numpy as np
import datetime
from extract_ad_info import extract_ad_info
from prediction_builder import create_predictions
from upload_data import upload_data
from static_data import MUNICIPALITY_TO_FA
from enrich_ads import months_between

def get_industry_data(ads, start_date=datetime.date(2006, 1, 1), max_date=datetime.date(2022, 7, 30)):
    num = (max_date - start_date).days
    complete_date = pd.to_datetime("1st of January, 2006") + pd.to_timedelta(np.arange(num), 'D')
    index = pd.DatetimeIndex(complete_date)
    industry_data = {"series": pd.Series([0] * num, index=index), "geos": {"faRegion": {}}}

    for ad in ads:
        date = ad["date"].split("T")[0].split(" ")[0] # To make sure date is yyyy-mm-dd
        year, month, day = date.split("-")
        days_from_max = (max_date - datetime.date(int(year), int(month), int(day))).days
        if(days_from_max < 0):
            continue
        try:
            industry_data["series"][date] += 1

            geo_name = ad["municipality"].lower().strip()
            if geo_name in MUNICIPALITY_TO_FA:
                geo_name = MUNICIPALITY_TO_FA[geo_name]
            else:
                continue

            if geo_name not in industry_data["geos"]["faRegion"]:
                industry_data["geos"]["faRegion"][geo_name] = {}

                for month in months_between(start_date, max_date):
                    industry_data["geos"]["faRegion"][geo_name][month.strftime("%Y-%m-%d")] = {
                        "num": 0,
                        "organisations_num": 0,
                        "details": {}
                    }

            if ad["employer"] in industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["details"]:
                industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["details"][ad["employer"]] += 1
                industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["num"] += 1
            else:
                industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["details"][ad["employer"]] = 1
                industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["organisations_num"] += 1
                industry_data["geos"]["faRegion"][geo_name][date[:-2]+"01"]["num"] += 1
        except Exception as err:
            print(err)


    industry_data = {"series": industry_data["series"].to_json(indent=4), "geos": industry_data["geos"]}

    return industry_data

if __name__ == "__main__":
    ads = []
    with open("ads/all_ads.json") as fp:
        ads = json.load(fp)

    if len(ads) == 0:
        all_ads = extract_ad_info()
        for ad_list in all_ads:
            ads.extend(ad_list)

        with open("ads/all_ads.json", "w") as fp:
            json.dump(ads, fp)


    industry_data = get_industry_data(ads)

    geo_data = industry_data["geos"]

    industry_data = create_predictions(industry_data["series"])
    industry_data.pop("eval_forecast")
    industry_data.pop("backtest")

    industry_data["geos"] = geo_data

    industry_data["num"] = industry_data["ad_series"]["values"][len(industry_data["ad_series"]["values"]) - 1]
    upload_data(industry_data, "bransch")
