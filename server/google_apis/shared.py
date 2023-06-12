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

sheet_id = None

def set_form_id(formId):
    global form_id
    form_id = formId

def set_sheet_id(sheetId):
    global sheet_id
    sheet_id = sheetId

def set_question_id(questionId):
    global question_id
    question_id = questionId

def get_form_id():
    global form_id
    return form_id

def get_sheet_id():
    global sheet_id
    return sheet_id

def get_question_id():
    global question_id
    return question_id

def get_service_name():
    global service_name
    return service_name

def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/forms',
              'https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/spreadsheets']
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
    services = ['form', 'sheet']
    services_version = ['v1', 'v4']
    real_service, real_version = None, None
    for index, service in enumerate(services):
        if not nameOfService.find(service): # Not is done to signify the searched word was found
            real_service = service
            if real_service.__eq__('form') or real_service.__eq__('sheet'):
                real_service += 's'
            real_version = services_version[index]
            break
    return real_service, real_version

def get_service(nameOfService):
    global current_service
    if current_service and nameOfService is None:
        return
    global service_name
    if "form" in nameOfService or "Form" in nameOfService:
        nameOfService = 'forms'
    elif "sheet" in nameOfService or "Sheet" in nameOfService:
        nameOfService = 'sheets'
    else:
        raise Exception("Please specify a valid service first.")
    if current_service is None or not nameOfService.__eq__(service_name):
        service_name, version = construct_service(nameOfService)
        global creds
        if creds is None:
            get_credentials()
        service = build(service_name, version, credentials=creds)
        current_service = service
        print("SUCCESSFULLY CREATED SERVICE")
    return current_service, service_name

def reset_service():
    global current_service
    current_service = None
