import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)
sqsClient = boto3.client("sqs")
# --- Helpers that build all of the responses ---
def sendMsg(values):
    # Send message to SQS queue
    queue_url = 'https://sqs.us-east-1.amazonaws.com/230009423205/Q1'
    Attributes={
        'people': {
            'DataType': 'String',
            'StringValue': values["people"]
        },
        'time': {
            'DataType': 'String',
            'StringValue': values["time"]
        },
        'email': {
            'DataType': 'String',
            'StringValue': values["email"]
        },
        'location' : {
            'DataType': 'String',
            'StringValue': values["location"]
        },
        'cuisine': {
            'DataType': 'String',
            'StringValue': values["cuisine"]
        }
    }
    response = sqsClient.send_message(
        QueueUrl=queue_url,
        MessageAttributes=Attributes,
        MessageBody='msg'
        )

def close(session_attributes, message):
    response = {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
        },
        'messages': [
            {
                'contentType': 'PlainText', 
                'content': message
                
            }
        ]
    }
    return response


def elicitIntent(session_attributes, message):
    responese =  {
    'sessionState': {
        
        "sessionAttributes":session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
        },
    },
    'messages': [
          {
              'contentType': 'PlainText',
              'content': message
            }
        ]
    }    

    return responese

def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n
    
def isvalid_cuisine(cuisine):
    cuisines = ['french', 'indian', 'chinese', 'japanese', 'mexican']
    return cuisine.lower() in cuisines

def isvalid_people(people):
    people = safe_int(people) 
    return people>0 and people<=100



def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message':  message_content
    }

 
def validate_dining_option(slot):
    if "cuisine" in slot and not isvalid_cuisine(slot["cuisine"]):
            return build_validation_result(False, "cuisine", "Available cuisine options: french, indian, chinese, japanese, mexican,")
            
    if "people" in slot and not isvalid_people(slot["people"]):
        return build_validation_result(False, 'people', 'Invalid number of people (max people: 100)')
            
    return build_validation_result(True, '', '')

  
    
def lambda_handler(event, context):
    logger.info(event['sessionState']["sessionAttributes"])
    return dispatch(event)

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    slots = intent_request['sessionState']['intent']['slots']
    
    filled_slot = {}
    location = None
    if "location" in slots and slots["location"]:
        location = slots['location']["value"]["interpretedValue"]
        filled_slot["location"] = location

    time = None
    if "time" in slots and slots["time"]:
        if "interpretedValue" in slots['time']["value"]:
            time = slots['time']["value"]["interpretedValue"]
            filled_slot["time"] = time

    cuisine = None
    if "cuisine" in slots and slots["cuisine"]:
        cuisine = slots['cuisine']["value"]["interpretedValue"]
        filled_slot["cuisine"] = cuisine

        
    people = None
    if "people" in slots and slots["people"]:
        people = slots['people']["value"]["interpretedValue"]
        filled_slot["people"] = people


    email = None
    if "email" in slots and slots["email"]:
        email = slots['email']["value"]["interpretedValue"]
        filled_slot["email"] = email

    
    all_slots = ["email", "location", "cuisine", "time", "people"]
    sessionAttributes = intent_request['sessionState']["sessionAttributes"]

    validation_result = validate_dining_option(filled_slot)
    if not validation_result['isValid']:
        return elicitIntent(sessionAttributes,validation_result['message'])
    
    interpretation = {"email":"What is your email address?",
                      "time":"When do you want to have your meal?",
                      "location":"What is your current location?",
                      "people":"How many people do you have?",
                      "cuisine":"What cuisine would you like?"}
    fullname = {"email":"email address",
                "time":"dining time",
                "location":"location",
                "people":"number of people",
                "cuisine":"cuisine type"}
    confirmation = ""
    if filled_slot:
        key = list(filled_slot.keys())[0]
        sessionAttributes[key]=filled_slot[key]
        confirmation = "Confirm your "+fullname[key]+": "+str(filled_slot[key]+".\n")

    logger.info(sessionAttributes)

    for slot in all_slots:
        if slot not in sessionAttributes:
            return elicitIntent(sessionAttributes,confirmation+interpretation[slot])

    
    
    sendMsg(sessionAttributes)
    return elicitIntent({}, "Thank you. I've got all necessary info. Sending restaurant suggestions.")
