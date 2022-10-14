import boto3
import json
import uuid
# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    ip = event["headers"]["X-Forwarded-For"]
    msg_from_user = event["body"]['messages'][0]["unstructured"]["text"]
    # change this to the message that user submits on 
    # your website using the 'event' variable
    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='7HBUPQREAZ', # MODIFY HERE
            botAliasId='P6YF33B6N4', # MODIFY HERE
            localeId='en_US',
            sessionId=str(hash(ip)),
            text=msg_from_user)
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        resp = {
            'statusCode': 200,
            'body': json.dumps({
                "messages": [
                    {
                    "type": "structured",
                    "structured": {
                        "id": "string",
                        "text": msg_from_lex[0]['content'],
                        "timestamp": "string",
                        "type": "product"
                        }
                    }
                ]
            })
        }
        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket
        return resp
