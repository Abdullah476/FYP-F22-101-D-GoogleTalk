from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import os
import json

creds = None
current_service = None
service_name = None

form_id = None
question_id = None

def set_form_id(formId):
    global form_id
    form_id = formId

def set_question_id(questionId):
    global question_id
    question_id = questionId

def get_form_id():
    global form_id
    return form_id

def get_question_id():
    global question_id
    return question_id

def get_service_name():
    global service_name
    return service_name

def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/forms',
              'https://www.googleapis.com/auth/drive']
    try:
        global creds
        if creds is None:
            file = json.load(open(os.environ['GOOGLE_APPLICATION_CREDENTIALS']))
            creds = service_account.Credentials.from_service_account_info(file, scopes=SCOPES)
        return creds
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def construct_service(nameOfService):
    services = ['form']
    services_version = ['v1']
    real_service, real_version = None, None
    for index, service in enumerate(services):
        if not nameOfService.find(service): # Not is done to signify the searched word was found
            real_service = service
            if real_service.__eq__('form'):
                real_service += 's'
            real_version = services_version[index]
            break
    return real_service, real_version

def get_service(nameOfService):
    global current_service
    global service_name
    if current_service is None:
        serviceName, version = construct_service(nameOfService)
        global creds
        if creds is None:
            get_credentials()
        service = build(serviceName, version, credentials=creds)
        current_service = service
        service_name = serviceName
        print("SUCCESSFULLY CREATED SERVICE")
    return current_service, service_name

def reset_service():
    global current_service
    current_service = None