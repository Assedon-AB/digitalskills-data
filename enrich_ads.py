import json
import requests
import pandas as pd
import numpy as np
from spinner import Spinner

def save_data_to_json(enriched_data):
    data_json = enriched_data.copy()
    for key in enriched_data.keys():
        data_json[key]["series"] = enriched_data[key]["series"].to_json(indent=4)

    with open(f"enriched/2020-enriched-jobs.json", "w", encoding="utf-8") as fd:
        json.dump(data_json, fd, ensure_ascii=False, indent=4)

def enrich_ads(documents_input):
    occupations = {}

    print(f"> Running Enrichment API on ads data")
    spinner = Spinner()
    spinner.start()
    try:
        headers = {
            "api-key": "YidceGExXHhhN1x4YzdceGY1VCtceDA0S1x4MDJ3WWNceDkwXHhlNFx4ZTRceGM1XHhhOFx4MGI5XHhiNic",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        i = 0
        adId = 0
        while len(documents_input) >= 100:
            i+=1
            body = json.dumps({
                "documents_input": documents_input[:100],
                "include_terms_info": False,
                "include_sentences": False,
                "sort_by_prediction_score": "NOT_SORTED"
            })
            req =  requests.post("https://jobad-enrichments-api.jobtechdev.se/enrichtextdocuments", data=body, headers=headers) # this will make the method "POST"
            resp = req.json()

            num = 5661 # TODO: Change from hardcoded num -> dynamic value
            complete_date = pd.to_datetime("1st of January, 2006") + pd.to_timedelta(np.arange(num), 'D')
            index = pd.DatetimeIndex(complete_date)

            for idx, ad in enumerate(resp):
                try:
                    occupations_found = []
                    for occupation in ad["enriched_candidates"]["occupations"]:
                        occupation_name = occupation["concept_label"].lower().strip()
                        if occupation["prediction"] >= 0.8:
                            if occupation_name not in occupations:
                                occupations[occupation_name] = { "series": pd.Series([0] * num, index=index), "employers": {} }

                            adObj = None
                            if ad["doc_id"] != "None":
                                adObj = next((x for x in documents_input[:100] if x["doc_id"] == ad["doc_id"]))
                            else:
                                adObj = documents_input[:100][idx]

                            if adObj:
                                date = adObj["date"].split("T")[0].split(" ")[0]
                                occupations[occupation_name]["series"][date] += 1

                                if adObj["employer"] in occupations[occupation_name]["employers"]:
                                    occupations[occupation_name]["employers"][adObj["employer"]] += 1
                                else:
                                    occupations[occupation_name]["employers"][adObj["employer"]] = 1


                                if "adIds" not in occupations[occupation_name]:
                                    occupations[occupation_name]["adIds"] = [adId]
                                else:
                                    occupations[occupation_name]["adIds"].append(adId)
                                adId += 1

                                if "count" in occupations[occupation_name]:
                                    occupations[occupation_name]["count"] += 1
                                else:
                                    occupations[occupation_name]["count"] = 1

                                for occ in occupations_found:
                                    if "similiar_jobs" not in occupations[occupation_name]:
                                        occupations[occupation_name]["similiar_jobs"] = {}

                                    if occ in occupations[occupation_name]["similiar_jobs"]:
                                        occupations[occupation_name]["similiar_jobs"][occ] += 1
                                    else:
                                        occupations[occupation_name]["similiar_jobs"][occ] = 1

                                occupations_found.append(occupation_name);

                                for trait in ad["enriched_candidates"]["traits"]:
                                    trait_name= trait["concept_label"].lower().strip()
                                    if "traits" not in occupations[occupation_name]:
                                        occupations[occupation_name]["traits"] = {}

                                    if trait_name in occupations[occupation_name]["traits"]:
                                        occupations[occupation_name]["traits"][trait_name] += 1
                                    else:
                                        occupations[occupation_name]["traits"][trait_name] = 1

                                for geo in ad["enriched_candidates"]["geos"]:
                                    geo_name = geo["concept_label"].lower().strip()
                                    if "geos" not in occupations[occupation_name]:
                                        occupations[occupation_name]["geos"] = {}

                                    if geo_name in occupations[occupation_name]["geos"]:
                                        occupations[occupation_name]["geos"][geo_name] += 1
                                    else:
                                        occupations[occupation_name]["geos"][geo_name] = 1

                except Exception as err:
                    print("Error:", err)

            documents_input = documents_input[100:]

        save_data_to_json(occupations)
        spinner.stop()
        return occupations
    except:
        save_data_to_json(occupations)
        spinner.stop()
        return occupations

if __name__ == "__main__":
    with open("ads/2020.json", "r") as fd:
        documents_input = json.load(fd)
        enrich_ads(documents_input)
