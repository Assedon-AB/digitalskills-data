import json
import requests

ads = []
occupations = []
traits = []
geos = []

try:
    with open("ads/2008.json", "r") as fd:
        documents_input = json.load(fd)

        headers = {
            "api-key": "YidceGExXHhhN1x4YzdceGY1VCtceDA0S1x4MDJ3WWNceDkwXHhlNFx4ZTRceGM1XHhhOFx4MGI5XHhiNic",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        i = 0
        while len(documents_input) >= 100:
            i+=1
            print(f"Running round {i}")
            body = json.dumps({
                "documents_input": documents_input[:100],
                "include_terms_info": False,
                "include_sentences": False,
                "sort_by_prediction_score": "NOT_SORTED"
            })
            req =  requests.post("https://jobad-enrichments-api.jobtechdev.se/enrichtextdocuments", data=body, headers=headers) # this will make the method "POST"
            resp = req.json()
            for idx, ad in enumerate(resp):
                for occupation in ad["enriched_candidates"]["occupations"]:
                    occupation_name = occupation["concept_label"].lower().strip()
                    occupations.append({
                        "label": occupation_name,
                        "prediction": occupation["prediction"]
                    })

                for trait in ad["enriched_candidates"]["traits"]:
                    trait_name= trait["concept_label"].lower().strip()
                    traits.append({
                        "label": trait_name,
                        "prediction": trait["prediction"]
                    })

                for geo in ad["enriched_candidates"]["geos"]:
                    geo_name= geo["concept_label"].lower().strip()
                    geos.append({
                        "label": geo_name,
                        "prediction": geo["prediction"]
                    })

            documents_input = documents_input[100:]

        # Go throug the last documents
        body = json.dumps({
            "documents_input": documents_input[:100],
            "include_terms_info": False,
            "include_sentences": False,
            "sort_by_prediction_score": "NOT_SORTED"
        })
        req =  requests.post("https://jobad-enrichments-api.jobtechdev.se/enrichtextdocuments", data=body, headers=headers) # this will make the method "POST"
        resp = req.json()
        for idx, ad in enumerate(resp):
            for occupation in ad["enriched_candidates"]["occupations"]:
                occupation_name = occupation["concept_label"].lower().strip()
                occupations.append({
                    "label": occupation_name,
                    "prediction": occupation["prediction"]
                })

            for trait in ad["enriched_candidates"]["traits"]:
                trait_name= trait["concept_label"].lower().strip()
                traits.append({
                    "label": trait_name,
                    "prediction": trait["prediction"]
                })

            for geo in ad["enriched_candidates"]["geos"]:
                geo_name= geo["concept_label"].lower().strip()
                geos.append({
                    "label": geo_name,
                    "prediction": geo["prediction"]
                })

    with open("enriched/2020-enriched-traits.json", "w") as fd:
        json.dump(traits, fd, ensure_ascii=False, indent=4)

    with open("enriched/2020-enriched-geos.json", "w") as fd:
        json.dump(geos, fd, ensure_ascii=False, indent=4)

    with open("enriched/2020-enriched-jobs.json", "w") as fd:
        json.dump(occupations, fd, ensure_ascii=False, indent=4)
except:
    with open("enriched/2020-enriched-jobs.json", "w") as fd:
        json.dump(occupations, fd, ensure_ascii=False, indent=4)

    with open("enriched/2020-enriched-traits.json", "w") as fd:
        json.dump(traits, fd, ensure_ascii=False, indent=4)

    with open("enriched/2020-enriched-geos.json", "w") as fd:
        json.dump(geos, fd, ensure_ascii=False, indent=4)
