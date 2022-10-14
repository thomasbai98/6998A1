import json
f = open('data.json', 'r')
data = json.load(f)
from datetime import datetime

ret = []
def insert_data(data_list, db=None, table='yelp-restaurants'):

    # overwrite if the same index is provided
    for data in data_list:
        useful_data = {}
        useful_data["id"] = data["id"]
        useful_data["name"] = data["name"]
        useful_data["cuisine"] = data["cuisine"]
        useful_data["review_count"] = data["review_count"]
        useful_data["rating"] = str(data["rating"])
        useful_data["latitude"] = str(data["coordinates"]["latitude"])
        useful_data["longitude"] = str(data["coordinates"]["longitude"])

        useful_data["address"] = data["location"]["address1"]
        useful_data["zip_code"] = data["location"]["zip_code"]
        ret.append(useful_data)
    # print('@insert_data: response', response)

insert_data(data["businesses"])
res = {"res":ret}
with open('dynamodb_data.json', 'w') as fp:
    json.dump(res, fp)