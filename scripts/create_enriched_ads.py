import json
import requests
import time

print("starting script...")


print("preparing ads...")

years = ["2013","2014","2015","2016","2017","2018","2019","2020","2021"]




for year in years:
    with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/ads/{}.json'.format(year)) as json_file:
        ad_data = json.load(json_file)
    documents_input = []
    if len(ad_data['it_ads']) > 0:
        for ad in ad_data['it_ads']:
            if(ad["description"]["text"]):
                documents_input.append({
                    "date": ad["publication_date"],
                    "doc_id": ad["id"],
                    "doc_headline": ad["headline"].lower(),
                    "doc_text": ad["description"]["text"].replace("\n\n", "").replace("\n", " ").lower()
                })
        print("_____________________")
        print("Length of documents_input")
        print(len(documents_input))
        print("_____________________")
        print("saving documents_input...")
        with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/enriched/input/{}_input.json'.format(year), 'w') as fp:
            json.dump({'documents_input': documents_input}, fp)
        print("documents_input saved!")
        enriched_results = []
        raw_response = []

        print("trying enriched...")
        try:

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

                    raw_response.append(ad)

                    temp_ad_obj = {}
                    temp_ad_obj['publication_date'] = documents_input[idx]['date']
                    temp_ad_obj['id'] = documents_input[idx]["doc_id"]
                    temp_occupations_list = []
                    for occupation in ad["enriched_candidates"]["occupations"]:
                        occupation_name = occupation["concept_label"].lower().strip()
                        temp_occupations_list.append({
                            "label": occupation_name,
                            "prediction": occupation["prediction"]
                        })
                    temp_ad_obj['occupations'] = temp_occupations_list
                    temp_skills_list = []
                    for skill in ad["enriched_candidates"]["competencies"]:
                        skill_name = skill["concept_label"].lower().strip()
                        temp_skills_list.append({
                            "label": skill_name,
                            "prediction": skill["prediction"]
                        })
                    temp_ad_obj['skills'] = temp_skills_list

                    temp_traits_list = []
                    for trait in ad["enriched_candidates"]["traits"]:
                        trait_name = trait["concept_label"].lower().strip()
                        temp_traits_list.append({
                            "label": trait_name,
                            "prediction": trait["prediction"]
                        })
                    temp_ad_obj['traits'] = temp_traits_list

                    enriched_results.append(temp_ad_obj)
                

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
                raw_response.append(ad)

                temp_ad_obj = {}
                temp_ad_obj['publication_date'] = documents_input[idx]['date']
                temp_ad_obj['id'] = documents_input[idx]["doc_id"]
                temp_occupations_list = []
                for occupation in ad["enriched_candidates"]["occupations"]:
                    occupation_name = occupation["concept_label"].lower().strip()
                    temp_occupations_list.append({
                        "label": occupation_name,
                        "prediction": occupation["prediction"]
                    })
                temp_ad_obj['occupations'] = temp_occupations_list
                temp_skills_list = []
                for skill in ad["enriched_candidates"]["competencies"]:
                    skill_name = skill["concept_label"].lower().strip()
                    temp_skills_list.append({
                        "label": skill_name,
                        "prediction": skill["prediction"]
                    })
                temp_ad_obj['skills'] = temp_skills_list

                temp_traits_list = []
                for trait in ad["enriched_candidates"]["traits"]:
                    trait_name = trait["concept_label"].lower().strip()
                    temp_traits_list.append({
                        "label": trait_name,
                        "prediction": trait["prediction"]
                    })
                temp_ad_obj['traits'] = temp_traits_list
                enriched_results.append(temp_ad_obj)
            #save raw
            #save input
            #save processed
            
            print("saving raw_response...")
            print(len(raw_response))
            with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/enriched/raw/{}_raw.json'.format(year), 'w') as fp:
                json.dump({'raw_response': raw_response}, fp)
            print("raw_response saved!")

            print("saving enriched_results...")
            print(len(enriched_results))
            with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/enriched/processed/{}_processed.json'.format(year), 'w') as fp:
                json.dump({'enriched_results': enriched_results}, fp)
            print("enriched_results saved!")
        except:
            print("saving raw_response...")
            print(len(raw_response))
            with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/enriched/raw/{}_raw.json'.format(year), 'w') as fp:
                json.dump({'raw_response': raw_response}, fp)
            print("raw_response saved!")

            print("saving enriched_results...")
            print(len(enriched_results))
            with open('/Users/andreassamuelsson/Projects/Assedon/digspec-data/enriched/processed/{}_processed.json'.format(year), 'w') as fp:
                json.dump({'enriched_results': enriched_results}, fp)
            print("enriched_results saved!")


print("All done!")