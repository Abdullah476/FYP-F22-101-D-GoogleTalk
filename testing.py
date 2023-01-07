from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import os
import json
import webbrowser

creds = None
service = None
drive_service = None

def get_drive_service(credentials):
    try:
        global drive_service
        if drive_service is None:
            service = build("drive", "v3", credentials=credentials)
            drive_service = service
            return service
        return drive_service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def share_file_with_user(file_id, user):
    try:
        permissions = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': user
        }
        global drive_service
        drive_service = get_drive_service(get_credentials())
        # sendNotificationEmail has to be false, otherwise it threw a "inappropriate content" error for some reason
        drive_service.permissions().create(fileId=file_id, body=permissions, sendNotificationEmail=False).execute()
        return True
    except HttpError as error:
        print(f"An error occured: {error}")

def delete_file(file_id):
    global drive_service
    try:
        drive_service = get_drive_service(get_credentials())
        drive_service.files().delete(fileId=file_id).execute()
        return True
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False

def get_credentials():
    global creds
    SCOPES = ['https://www.googleapis.com/auth/forms',
              'https://www.googleapis.com/auth/drive']
    try:
        if creds is None:
            file = json.load(open(os.environ['GOOGLE_APPLICATION_CREDENTIALS']))
            creds = service_account.Credentials.from_service_account_info(file, scopes=SCOPES)
        return creds
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_service(creds):
    global service
    if service is None:
        service = build('forms', 'v1', credentials=creds)
    return service

def create_form(title="Untitled Form"):
    global service
    body = {
        "info": {
            "title": title,
            "documentTitle": title
        }
    }
    try:
        service = get_service(get_credentials())
        form = service.forms().create(body=body).execute()
        # Share form with logged in user
        form_id = form['formId']
        share_file_with_user(form_id, 'icyguy8@gmail.com')
        link = "https://docs.google.com/forms/d/" + form['formId']
        webbrowser.open(link)
        return form
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def create_question(form_id, question_name="Untitled Question", extra_info=None):
    global service
    try:
        service = get_service(get_credentials())
        if form_id is None:
            raise Exception("Please select a form to add a question to first.")
        formObject = service.forms().get(formId=form_id).execute()
        idx = 0
        if 'items' in formObject.keys():
            idx = len(formObject['items'])
        newQuestion = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': question_name,
                        'description': None,
                        'questionItem': {
                            'question': {
                                'required': False,
                                'choiceQuestion': {
                                    'type': 'RADIO',
                                    'options': [
                                        {'value': 'Option 1'}
                                    ],
                                    'shuffle': False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": idx
                    }
                }
            }]
        }
        done = service.forms().batchUpdate(formId=form_id, body=newQuestion).execute()
        print(done)
        return done
    except HttpError as error:
        print(error)
        return None

def get_form_object(form_id):
    formObject = service.forms().get(formId=form_id).execute()
    return formObject

def delete_form(title):
    global service
    service = get_service(get_credentials())
    form_id = get_form_by_name(title)
    if form_id is None:
        print("No such Forms exists.")
        return False
    return delete_file(form_id)

def get_form_by_name(formName):
    service = get_drive_service(get_credentials())
    form_id = None
    try:
        while True:
            page_token = None
            found = False
            responses = service.files().list(
                q="mimeType='application/vnd.google-apps.form'",
                spaces='drive',
                fields='nextPageToken, files(id,name)',
                pageToken=page_token
                ).execute()
            for i in responses.get('files', []):
                if i.get('name').__eq__(formName):
                    form_id = i.get('id')
                    found = True
                    break
            if found:
                break
            page_token = responses.get('nextPageToken', None)
            if page_token is None:
                break
        return form_id
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def add_option(form_id, question_id, value):
    formObject = service.forms().get(formId=form_id).execute()
    for index, item in enumerate(formObject['items']):
        question = item['questionItem']['question']
        if question['questionId'].__eq__(question_id):
            if 'choiceQuestion' in question.keys():
                newOption = {'value': value}
                itemToUpdate = item
                itemToUpdate['questionItem']['question']['choiceQuestion']['options'].append(newOption)
                updateRequest = {
                    'requests': [{
                        'updateItem': {
                            'item': itemToUpdate,
                            'location': {
                                'index': index
                            },
                            'updateMask': 'questionItem.question.choiceQuestion.options',
                        }
                    }]
                }
                global service
                service = get_service(get_credentials())
                done = service.forms().batchUpdate(formId=form_id, body=updateRequest).execute()
                print(done)
                return done
    return None

if __name__ == "__main__":
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getcwd() + "\\google_apis\\service_account_credentials.json"
    #form = create_form("Testing")
    #question = create_question(form['formId'], "Another test")
    #formObject = get_form_object(form["formId"])
    #questionId = formObject['items'][0]['questionItem']['question']['questionId']
    #add_option(form['formId'], questionId, 'Option 2')
    delete_form("Testing")
