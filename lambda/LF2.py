import boto3
import json
import requests
import random
from requests_aws4auth import AWS4Auth

def sqsGet():
    sqs = boto3.client('sqs')
    response = sqs.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/230009423205/Q1',
        MaxNumberOfMessages=5,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )
    return response

def sqsDel(handler):
    sqs = boto3.client('sqs')
    response = sqs.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/230009423205/Q1',
        ReceiptHandle=handler
    )
    return response 

def opensearch(cuisine):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session(aws_access_key_id="",
                                aws_secret_access_key="", 
                                region_name="us-east-1").get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'https://search-restaurants-zs6ab6wsxaeejin4qpoyz4vc4u.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = host + '/' + index + '/_search'    
    query = {
        "size": 1000,
        "query": {
            "query_string": {
                "default_field": "cuisine",
                "query": cuisine
            }
        }
    }
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    numHits = res['hits']['total']
    hits = res['hits']['hits']
    ids = []
    for hit in hits:
        ids.append(str(hit['_source']['id']))
    return ids


def dynamodbSearch(ids,cuisine):
    res = []
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')
    for id in ids:
        response = table.get_item(Key={"id":id,'cuisine':cuisine})

        res.append(response["Item"])
    return res


def lambda_handler(event, context):
    cuisineInterpretation = {"french":"french","chinese":"chinese","indian":"indpak","japanese":"japanese","mexican":"mexican"}
    sqsResponses = sqsGet()
    if "Messages" in sqsResponses:
        for message in sqsResponses['Messages']:
            cuisine = message['MessageAttributes']['cuisine']['StringValue']

            ids = opensearch(cuisineInterpretation[cuisine])

            ids = random.sample(ids, 1)

        

            datas = dynamodbSearch(ids,cuisineInterpretation[cuisine])

            msg = ("Resturant name: " + datas[0]['name'] +
                    ".\nLocation: " + datas[0]['address'] + 
                    ".\nRating: "+datas[0]['rating'] + 
                    ".\nNumber of people: " + message['MessageAttributes']['people']['StringValue'] +
                    ".\nTime: "+ message['MessageAttributes']['time']['StringValue'])
            emailcontent = {'Subject' : {'Data' : "Resturant Recommendation"},'Body': {'Text' : {'Data' : msg}}}
            fromemail = "yb2519@columbia.edu"
            toemail = message['MessageAttributes']['email']['StringValue']
            print(toemail)
            client = boto3.client('ses')
            
            sqsDel(message['ReceiptHandle'])
            response = client.send_email(Source=fromemail,Destination={"ToAddresses":[toemail]},Message = emailcontent)
            

