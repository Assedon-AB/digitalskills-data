
import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np

print("starting script...")


print("preparing ads...")

years = ["2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
for year in years:
    temp_list = []
    print("starting " + year + "...")
    with open('/Users/andreassamuelsson/Projects/Jobtechdev/UKA-Sandbox/{}.json'.format(year)) as json_file:
        ad_data = json.load(json_file)
    for ad in ad_data:
        if ad["occupation_field"]["concept_id"] == "apaJ_2ja_LuF":
            temp_list.append(ad)
    
    print(len(temp_list))
    with open('/Users/andreassamuelsson/Projects/Jobtechdev/digspec-data/ads/{}.json'.format(year), 'w') as fp:
        json.dump({'it_ads': temp_list}, fp)




print("done!")