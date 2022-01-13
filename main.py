from extract_ad_info import extract_ad_info
from extract_skills import extract_skills
from enrich_ads import enrich_ads
from relationship_builder import create_relationships

def main():
    # Filtrera annonser.
    all_ads = extract_ad_info()
    ads = []
    for ad_list in all_ads:
        ads.extend(ad_list)

    # Extrahera kompetenser
    skills_data = extract_skills(ads)
    # Extrahera yrke och mjukavärden
    enriched_data = enrich_ads(ads)

    # Skapa relationer mellan kompetenser, yrke och mjukvärden.
    skills_data, jobs_data = create_relationships(skills_data, enriched_data)
    print(skills_data)
    print(jobs_data)

    # Skapa en prognos av yrken och kompetenser -> skills-prediction.py
    # Spara ner slutresultatet i en databas.
        # Fil som använder sig av POST routes i API
    pass

if __name__ == "__main__":
    main()
