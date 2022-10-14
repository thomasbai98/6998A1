# importing the requests library
import requests
from requests.auth import HTTPBasicAuth
# api-endpoint
URL = "https://api.yelp.com/v3/businesses/search"
import json
ret = {"businesses":[]}
cuisines = ["french","indpak","chinese","japanese","mexican"]
ids = set({})
for cuisine in cuisines:
    PARAMS = {'location': "nyc","limit":50,"categories":cuisine}
    headers = {"Authorization": "Bearer kwvHISjiuRvDwDVzh3v06Y_r4OcSAuNz_CDOu9SlQoSK5bliFnWBiMQJnrxr5YleOdSeDIuFXTA6kp0PHFnMZ2so48epNoDbc2z03uI9TnnFQD0Ex8m5qNPOOhlCY3Yx"}
    for offset in range(0,10):
        PARAMS["offset"]=offset*60
        r = requests.get(url=URL, params=PARAMS,headers=headers)

    # extracting data in json format
        data = r.json()
        for item in data["businesses"]:
            item["cuisine"] = cuisine
            if (item["id"],cuisine) not in ids:
                ret["businesses"].append(item)
                ids.add((item["id"],cuisine))

# printing the output

with open('data.json', 'w') as fp:
    json.dump(ret, fp)