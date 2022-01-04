from extract_ad_info import extract_ad_info
from extract_skills import extract_skills
from enrich_ads import enrich_ads

def main():
    # Filtrera annonser.
    all_ads = extract_ad_info()
    ads = []
    for ad_list in all_ads:
        ads.extend(ad_list)

    # Extrahera kompetenser
    skills_data = extract_skills(ads)
    # Extrahera kompetens, yrke och mjukavärden
    enriched_data = enrich_ads(ads)
    
    print("Skills data", skills_data)
    print("Enriched data", enriched_data)

    # Bygg relationer mellan kompetenser, yrke och mjukvärden. -> relationship-builder.py
    # Skapa en prognos av yrken och kompetenser -> skills-prediction.py
    # Spara ner slutresultatet i en databas.
        # Fil som använder sig av POST routes i API
    pass

if __name__ == "__main__":
    main()
