import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

def lambda_handler(event, context):
    insert_data(event["res"])
    return

def insert_data(data_list, db=None, table='yelp-restaurants'):
    count = 0
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    count = 0
    for data in data_list:
        count += 1
        data["insertAtTimestamp"] = datetime.now().strftime("%H:%M:%S")+"-"+str(count)
        response = table.put_item(Item=data)

    print(count)

