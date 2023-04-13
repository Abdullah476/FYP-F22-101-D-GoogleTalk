from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_apis.shared import get_credentials, get_service, get_sheet_id, set_sheet_id
from google_apis import drive
import webbrowser, string

sheets_service = None

# This function is somewhat hardcoded
# it expects the user to explicitly define both rows and columns (A1:C4 or D5:G26, not A:B3 or J:L)
# This will be fixed later on
def range_to_grid_range(_range):
    # First, split the A1 range into separate positions
    ranges = _range.split(':')
    # Now we have two positions that we can manipulate. Let's advance further
    letters, numbers = [], []
    letters.append(ranges[0].rstrip('0123456789')) # extract both columns
    letters.append(ranges[1].rstrip('0123456789'))
    numbers.append(ranges[0][len(letters[0]):]) # extract both numbers
    numbers.append(ranges[1][len(letters[1]):])
    # Now numbers will be our rows, and letters will be our columns
    for index, column in enumerate(letters):
        num = 0
        for letter in column: # For each letter
            if letter in string.ascii_letters:
                num = num * 26 + (ord(letter.upper()) - ord('A')) + 1
        letters[index] = num
    letters[0] -= 1 # This is done to ensure zero-based indexing for the left half
    # Numbers are far easier to convert
    numbers[0] = int(numbers[0]) - 1
    numbers[1] = int(numbers[1])
    # Now we have a Grid Range in the form of a list
    # startRowIndex, endRowIndex, startColumnIndex, endColumnIndex
    return [numbers[0], numbers[1], letters[0], letters[1]] 

# Function to create a new spreadsheet
def create_spreadsheet(title="Untitled"):
    global sheets_service
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    try:
        sheets_service, _ = get_service('sheets')
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet['spreadsheetId']
        set_sheet_id(spreadsheet_id)
        drive.share_file_with_user(spreadsheet_id, 'abdullahajaz51@gmail.com') # Same deal as in Forms.py
        link = "https://docs.google.com/spreadsheets/d/" + spreadsheet_id
        webbrowser.open(link)
        return spreadsheet
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

# Function to write to spreadsheet
def write_to_spreadsheet(range_name, values, value_input_option='USER_ENTERED', mode='w'): # Not required to change value_input_option, so can be removed nad implicitly passed
    global sheets_service
    try:
        sheets_service, _ = get_service('sheets')
        sheet_id = get_sheet_id()
        if sheet_id is None:
            raise Exception("Please select a sheet to write values to first.")
        body = {
            'values': [[values]]
        }
        result = None
        if mode == 'w':
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            # print(f"{result.get('updatedCells')} cells updated.")
        elif mode == 'a':
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            # print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def clear_from_spreadsheet(range_name):
    global sheets_service
    try:
        sheets_service, _ = get_service('sheets')
        sheet_id = get_sheet_id()
        if sheet_id is None:
            raise Exception("Please select a sheet to clear values from first.")
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=sheet_id, range=range_name).execute()
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def protect_range(_range, users = ['icyguy8@gmail.com']):
    global sheets_service
    try:
        sheets_service, _ = get_service('sheets')
        spreadsheet_id = get_sheet_id()
        if spreadsheet_id is None:
            raise Exception("Please select a sheet to protect ranges in first.")
        # Range here will be used as a GridRange. This is a special formatting of ranges for this command.
        # The execution is simple on smaller scales, but becomes exponentially difficult if not handled properly.
        # The methodology is to take a range, such as A1:B1 in A1 notation, and simply convert it to a numerical index.
        # Assume that we have A3:B5 in A1 notation
        # Then we will separate the columns first (A and B), then the numbers (3 and 5)
        # Keep in mind that the indexes are half-open, i.e. [startIndex, endIndex)
        # Convert each of them into zero-based indexes (A and 1 start from zero)
        # For example, A and B correspond to 0 and 1 respectively, but 1 is not included in the range, so we do +1 to B and get 2.
        # Similarly, 3 and 5 correspond to 2 and 4 respectively, but 4 is not included in the range when performing an operation,
        # so we do +1 to 4 and get 5.
        # As a result, we get four indices: startRowIndex (2), endRowIndex (5), startColumnIndex (0), endColumnIndex (2)
        # THIS will be used in our GridRange object, given below
        grid_range = range_to_grid_range(_range)
        # Currently, we're dealing with only one sheet ID, so this will be hardcoded
        sheets_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = sheets_metadata.get('sheets','')[0].get("properties", {}).get("sheetId", 0) # This is going to confuse a lot of people
        body = {
            "requests": [{
                "addProtectedRange": {
                    "protectedRange": {
                        "range": { # Define range specified by the user
                            "sheetId": sheet_id,
                            "startRowIndex": grid_range[0],
                            "endRowIndex": grid_range[1],
                            "startColumnIndex": grid_range[2],
                            "endColumnIndex": grid_range[3]
                        },
                        "editors": { # List of users for who the document will be protected
                            "users": users,
                            "groups": users,
                            "domainUsersCanEdit": True
                        }
                    }
                }}
            ]
        }
        return sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    except HttpError as error:
        print(f"An error occured: {error}")
        return error

#######################################################

# Function to get spreadsheet id from file
def get_spreadsheet_id(file_path):
    # Reading link of spreadsheet from file
    with open(file_path) as inFile:
        link = inFile.readline()

    # Tokenizing link of form to get its id
    tokens = link.split("/")
    return tokens[5]  # Second last token is id

#######################################################

def text_literal(text):
    # Remove everything from beginning and end until alphabet is hit
    for index in range(len(text)):
        if text[index].isalpha() or text[index].isnumeric():
            text = text[index:]
            break
    for index in range(len(text)-1, 0, -1):
        if text[index].isalpha() or text[index].isnumeric():
            text = text[:index+1]
            break
    return "".join([letter for letter in text if letter.isalpha() or letter.isnumeric() or letter == ' ']).lower()

def get_sheet_by_name(sheetName):
    service = drive.get_drive_service(get_credentials())
    sheet_id = None
    try:
        while True:
            page_token = None
            found = False
            responses = service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                spaces='drive',
                fields='nextPageToken, files(id,name)',
                pageToken=page_token
                ).execute()
            for i in responses.get('files', []):
                if text_literal(i.get('name')).__eq__(text_literal(sheetName)):
                    sheet_id = i.get('id')
                    print("Got it!")
                    found = True
                    break
            if found:
                break
            page_token = responses.get('nextPageToken', None)
            if page_token is None:
                break
        return sheet_id
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def select_sheet(sheet_name):
    sheets_service, _ = get_service('sheets')
    sheetId = get_sheet_by_name(sheet_name)
    if sheetId is not None:
        sheetObject = sheets_service.spreadsheets().get(spreadsheetId=sheetId).execute()
        print(sheetObject)
        return set_sheet_id(sheetId)
    raise Exception("Could not find the spreadsheet with the name '" + sheet_name + "'.")

def delete_spreadsheet(title):
    global sheets_service
    sheet_id = get_sheet_by_name(title)
    if sheet_id is None:
        print("No such Forms exists.")
        return False
    return drive.delete_file(sheet_id)