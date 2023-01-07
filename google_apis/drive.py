from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import os
import json
from google_apis.shared import get_credentials

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