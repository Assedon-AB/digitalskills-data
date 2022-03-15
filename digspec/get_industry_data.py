import json
import pandas as pd
import numpy as np
from extract_ad_info import extract_ad_info
from prediction_builder import create_predictions
from upload_data import upload_data

def get_industry_data(ads):
    num = 5844 # TODO: Change from hardcoded num -> dynamic value
    complete_date = pd.to_datetime("1st of January, 2006") + pd.to_timedelta(np.arange(num), 'D')
    index = pd.DatetimeIndex(complete_date)
    industry_data = {"series": pd.Series([0] * num, index=index)}

    for ad in ads:
        date = ad["date"].split("T")[0].split(" ")[0] # To make sure date is yyyy-mm-dd
        industry_data["series"][date] += 1

    industry_data = {"series": industry_data["series"].to_json(indent=4)}

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
    industry_data = create_predictions(industry_data["series"])
    industry_data.pop("series")
    industry_data.pop("eval_forecast")
    industry_data.pop("backtest")

    industry_data["num"] = industry_data["ad_series"]["values"][len(industry_data["ad_series"]["values"]) - 1]
    upload_data(industry_data, "bransch")
