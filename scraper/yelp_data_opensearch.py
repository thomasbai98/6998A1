import json
f = open('dynamodb_data.json', 'r')
data = json.load(f)
count = 1
fp = open('opensearch_data.json', 'w')
for item in data["res"]:
    index = {"index":{"_index":"restaurants","_id":count}}
    json.dump(index, fp)
    fp.write("\n")
    res = {"id":item["id"],"cuisine":item["cuisine"]}
    json.dump(res, fp)
    fp.write("\n")
    count += 1
fp.close()