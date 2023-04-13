from googleapiclient.errors import HttpError
import webbrowser, requests, re, json, pyautogui
from google_apis.shared import get_service, set_form_id, set_question_id, get_form_id, get_question_id, get_credentials
from google_apis import drive


# The two functions below are exclusively for form filling and submission

def refine(text):
    for index in range(len(text)):
        if text[index].isalpha() or text[index].isnumeric():
            return text[index:].capitalize()

def extract_questions(uri):
    html_data = requests.get(uri).text
    data = json.loads( re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', html_data, flags=re.S).group(1) )

    question_entry_ids = []
    for i in get_ids(data):
        if i is not None:
            question_entry_ids.append(str(i))
    return question_entry_ids

def get_ids(d):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from get_ids(v)
    elif isinstance(d, list):
        if len(d) > 1 and d[1] is None:
            yield d[0]
        else:
            for v in d:
                yield from get_ids(v)

forms_service = None

current_form = None
current_question = None

question_attributes = {
    'textQuestion': ['required', 'paragraph'],
    'scaleQuestion': ['required', 'low', 'high', 'lowLabel', 'highLabel'],
    'dateQuestion': ['required', 'includeYear', 'includeTime'],
    'timeQuestion': ['required', 'duration'],
    'choiceQuestion': ['required', 'type', 'shuffle']
}

attribute_type = {
    'RADIO': ['radio'],
    'CHECKBOX': ['check box', 'checkbox'],
    'DROP_DOWN': ['drop down', 'dropdown']
}

answers = {} # for form filling

def get_form_by_name(formName):
    service = drive.get_drive_service(get_credentials())
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
                if text_literal(i.get('name')).__eq__(text_literal(formName)):
                    form_id = i.get('id')
                    print("Got it!")
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

def create_form(title="Untitled Form"):
    global forms_service
    title = refine(title)
    body = {
        "info": {
            "title": title,
            "documentTitle": title
        }
    }
    try:
        forms_service, _ = get_service('forms')
        form = forms_service.forms().create(body=body).execute()
        # Share form with logged in user
        form_id = form['formId']
        set_form_id(form_id)
        drive.share_file_with_user(form_id, 'abdullahajaz51@gmail.com') # Email is hardcoded, but will be made generic by accessing Chrome's accounts info
        link = "https://docs.google.com/forms/d/" + form['formId']
        global answers
        answers = {}
        webbrowser.open(link)
        return form
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def create_textQuestion(paragraph=False):
    return {
        'required': False,
        'textQuestion': {
            'paragraph': paragraph
        }
    }

def create_choiceQuestion(choiceType='RADIO'):
    return {
        'required': False,
        'choiceQuestion': {
            'type': choiceType,
            'options': [
                {'value': 'placeholder'}
            ],
            'shuffle': False
        }
    }

def create_dateQuestion(dummy=None): # The dummies are placed temporarily to prevent any clashes
    return {
        'required': False,
        'dateQuestion': {
            'includeTime': False,
            'includeYear': False
        }
    }

def create_timeQuestion(dummy=None):
    return {
        'required': False,
        'timeQuestion': {
            'duration': False
        }
    }

def create_scaleQuestion(dummy=None):
    return {
        'required': False,
        'scaleQuestion': {
            'low': 1,
            'high': 10,
            'lowLabel': '',
            'highLabel': ''
        }
    }

functionsList = {
    'textQuestion': 'create_textQuestion',
    'choiceQuestion': 'create_choiceQuestion',
    'scaleQuestion': 'create_scaleQuestion',
    'dateQuestion': 'create_dateQuestion',
    'timeQuestion': 'create_timeQuestion'
}

def create_question(question_type, question_name="Untitled Question", extra_info=None, index=None):
    try:
        question_name = refine(question_name)
        forms_service, _ = get_service('forms')
        form_id = get_form_id()
        if form_id is None:
            raise Exception("Please select a form to add a question to first.")
        formObject = forms_service.forms().get(formId=form_id).execute()
        idx = 0

        if 'items' in formObject.keys():
            if index is None:
                idx = len(formObject['items'])
            else:
                idx = index
            
        # Experimental work
        global functionsList
        questionValue = globals()[functionsList[question_type]](extra_info)
        # Continue on track
        newQuestion = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': question_name,
                        'description': None,
                        'questionItem': {
                            'question': questionValue
                        }
                    },
                    "location": {
                        "index": idx
                    }
                }
            }]
        }
        updated_form = update_form(newQuestion)
        set_question_id(updated_form['replies'][0]['createItem']['questionId'][0])
        return updated_form
    except HttpError as error:
        print(error)
        return None
    
def delete_question(question_name='Untitled Question'):
    forms_service, _ = get_service('forms')
    form_id = get_form_id()
    if form_id is None:
        raise Exception("Please select a form to delete a question from first.")
    formObject = forms_service.forms().get(formId=form_id).execute()
    for index, item in enumerate(formObject['items']):
        if text_literal(item['title']).__eq__(text_literal(question_name)):
            deleteRequest = {
                'requests': [{
                    'deleteItem': {
                        'location': {
                            'index': index
                        }
                    }
                }]
            }
            return update_form(deleteRequest)
    raise Exception("No question of the name '" + question_name + "' exists")

def select_form(form_name):
    forms_service, _ = get_service('forms')
    formId = get_form_by_name(form_name)
    if formId is not None:
        formObject = forms_service.forms().get(formId=formId).execute()
        set_form_id(formId)
        questions = list_questions()
        question_entry_ids = extract_questions(formObject['responderUri'])
        global answers
        answers = {}
        for index, question in enumerate(questions):
            answers[question] = {}
            answers[question][question_entry_ids[index]] = None
        print(answers)
        return formObject
    raise Exception("Could not find the form with the name '" + form_name + "'.")

def select_question(question_name):
    forms_service, _ = get_service('forms')
    formId = get_form_id()
    if formId is None:
        raise Exception("Please select a form before selecting a question within it.")
    formObject = forms_service.forms().get(formId=formId).execute()
    for index, item in enumerate(formObject['items']):
        if text_literal(item['title']).__eq__(text_literal(question_name)):
            set_question_id(item['questionItem']['question']['questionId'])
            print("Selected!")
            return
    raise Exception("No question of the name '" + question_name + "' could be found.")


#########################################
# A byproduct from the previous iteration
def add_text_question_to_form(title="New Question", isParagraph=False):
    try:
        global forms_service
        forms_service = get_service('forms')
        global form_id
        if form_id is None:
            raise Exception("Please select a form to add a question to first.")
        formObject = forms_service.forms().get(formId=form_id).execute()
        idx = 0
        if 'items' in formObject.keys():
            idx = len(formObject['items'])
        question = {
            "requests": [{
            "createItem": {
                "item": {
                    "title": title,
                    "description": None,
                    "questionItem":{
                        "question": {
                            "required": False,
                            "textQuestion": {
                                "paragraph": isParagraph
                            }
                        }
                    }
                },
                "location": { # At what location do you want the question to be at?
                    "index": idx # Integer value
                }
            }
            }]
        }
        return update_form(question)
    except HttpError as error:
        print(f"An error occured: {error}")
        return None
#########################################

def get_option(value, optionType):
    value = text_literal(value)
    form_id = get_form_id()
    if form_id is None:
        raise Exception("No form was selected to make changes in.")
    question_id = get_question_id()
    if question_id is None:
        raise Exception("No question was selected to make changes in.")
    forms_service, _ = get_service('forms')
    formObject = forms_service.forms().get(formId=form_id).execute()
    for index, item in enumerate(formObject['items']):
        question = item['questionItem']['question']
        if question['questionId'].__eq__(question_id):
            if 'choiceQuestion' in question.keys():
                newItem = None
                if optionType.__eq__('add'):
                    newItem = add_option(item, value)
                elif optionType.__eq__('remove'):
                    newItem = remove_option(item, value)
                updateRequest = {
                    'requests': [{
                        'updateItem': {
                            'item': newItem,
                            'location': {
                                'index': index
                            },
                            'updateMask': 'questionItem.question.choiceQuestion.options',
                        }
                    }]
                }
                update_form(updateRequest)
    return None

def add_option(item, value):
    newOption = {'value': value}
    item['questionItem']['question']['choiceQuestion']['options'].append(newOption)
    return item

def remove_option(item, value):
    options = item['questionItem']['question']['choiceQuestion']['options']
    newOptions = [i for i in options if i['value'] != value]
    item['questionItem']['question']['choiceQuestion']['options'] = newOptions
    return item

def update_attribute(attribute, value):
    questionId = get_question_id()
    if questionId is None:
        raise Exception("Please select a question to update its attribute first.")
    formId = get_form_id()
    if formId is None:
        raise Exception("No form has been selected to perform any update operation.")
    forms_service, _ = get_service('forms')
    formObject = forms_service.forms().get(formId=formId).execute()
    for index, item in enumerate(formObject['items']):
        if item['questionItem']['question']['questionId'].__eq__(questionId):
            global question_attributes
            questionList = item['questionItem']['question'].keys()
            questionType = list(set(questionList).intersection(list(question_attributes.keys())))[0]
            if attribute not in question_attributes[questionType]:
                raise Exception("The attribute '" + attribute + "' does not exist in the question you want to update.")
            forNumber = ['low', 'high']
            forBool = ['paragraph', 'duration', 'includeYear', 'includeTime', 'shuffle']
            forString = ['lowLabel', 'highLabel', 'type']
            forRequired = ['required']
            trueValue = None
            if attribute in forNumber:
                from word2number.w2n import word_to_num
                try:
                    trueValue = word_to_num(value)
                except Exception as e:
                    raise Exception("The given value isn't a number.")
            elif attribute in forBool or attribute in forRequired:
                if 'false' in value:
                    trueValue = False
                elif 'true' in value:
                    trueValue = True
                else:
                    raise Exception("The given value must be either true or false.")
                if attribute.__eq__('required'):
                    item['questionItem']['question']['required'] = trueValue
                    updatedResponse = {
                        'requests': [{
                            'updateItem': {
                                'item': item,
                                'location': {
                                    'index': index
                                },
                                'updateMask': 'questionItem.question',
                            }
                        }]
                    }
                    return update_form(updatedResponse)
            elif attribute in forString:
                if attribute.__eq__('type'):
                    global attribute_type
                    for type in attribute_type.keys():
                        if text_literal(value) in attribute_type[type]:
                            trueValue = type
                            print(trueValue)
                            break
                    if trueValue is None:
                        raise Exception("You specified an incorrect choice type.")
                else:
                    trueValue = value
            item['questionItem']['question'][questionType][attribute] = trueValue
            updatedResponse = {
                'requests': [{
                    'updateItem': {
                        'item': item,
                        'location': {
                            'index': index
                        },
                        'updateMask': 'questionItem.question.'+questionType+'.'+attribute
                    }
                }]
            }
            return update_form(updatedResponse)
    raise Exception("No question has been selected to update its attribute.")

def update_form(body=None):
    forms_service, _ = get_service('forms')
    form_id = get_form_id()
    created_question = None
    if body is None:
        created_question = forms_service.forms().batchUpdate(formId=form_id).execute()
    else:
        created_question = forms_service.forms().batchUpdate(formId=form_id, body=body).execute()
    return created_question

def list_questions():
    forms_service, _ = get_service('forms')
    form_id = get_form_id()
    if forms_service and form_id:
        metadata = forms_service.forms().get(formId=form_id).execute()
        questions_list = []
        if metadata.get('items'):
            questions = metadata['items']
            for question in questions:
            #print(question['title'], question['questionItem']['question']['questionId'])
                questions_list.append(text_literal(question['title']))
        return questions_list
    raise Exception("Please select a form to list its questions.")

def show_answers():
    global answers
    for key, value in answers.items():
        print(key + " --- " + value[value.keys()[0]])

def update_page(service, id):
    url = service.forms().get(formId=id).execute()['responderUri']
    url += '?usp=pp_url&' # This is where prefilled entries will take place
    global answers
    print(answers)
    for answer in answers.values():
        if answer[list(answer.keys())[0]] is not None:
            url += ('entry.' + list(answer.keys())[0] + '=' + answer[list(answer.keys())[0]] + '&')
    url = url[:-1] # Now the prefilled link is prepared
    pyautogui.hotkey('ctrl', 'w')
    webbrowser.open(url)

def enter_answer(answer, question_name=None):
    global forms_service
    try:
        forms_service, _ = get_service('forms')
        form_id = get_form_id()
        if form_id:
            question_id = get_question_id()
            global answers
            current_questions = forms_service.forms().get(formId=form_id).execute()['items']
            if question_id and question_name is None: # If question selected, extract its question name and use it to append answer
                for question in current_questions:
                    if question_id.__eq__(question['questionItem']['question']['questionId']):
                        question_name = question['title']
                        answers[text_literal(question_name)][list(answers[text_literal(question_name)].keys())[0]] = refine(answer)
                        return update_page(forms_service, form_id)
                raise Exception("Could not find the question you selected in the form.")
            elif question_name: # Else simply insert answer in dictionary
                for question in current_questions:
                    if text_literal(question['title']).__eq__(text_literal(question_name)):
                        answers[text_literal(question_name)][list(answers[text_literal(question_name)].keys())[0]] = refine(answer)
                        return update_page(forms_service, form_id)
                raise Exception("The question you specified does not exist in the form.")
            raise Exception("Please either select or specify the question you wish to answer.")
        raise Exception("Please select a form to enter answer in first.")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

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


def submit_form():
    global forms_service
    if forms_service:
        form_id = get_form_id()
        try:
            if form_id:
                url = forms_service.forms().get(formId=form_id).execute()['responderUri']
                url = url.rsplit('/',1)[0]
                url += '/formResponse'
                url += '?usp=pp_url&'
                global answers
                for answer in answers.values():
                    if answer[list(answer.keys())[0]] is not None:
                        url += ('entry.' + list(answer.keys())[0] + '=' + answer[list(answer.keys())[0]] + '&')
                url = url[:-1] # Now the prefilled link is prepared
                pyautogui.hotkey('ctrl', 'w')
                return webbrowser.open(url)
            raise Exception("Please select a form to submit first..")
        except Exception as e:
            print(f"Error: {e}")
    else:
        raise Exception("Please specify a form to fill out")

def delete_form(title):
    global forms_service
    form_id = get_form_by_name(title)
    if form_id is None:
        print("No such Forms exists.")
        return False
    return drive.delete_file(form_id)