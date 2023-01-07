from nltk.corpus import wordnet
from google_apis.shared import get_credentials, get_service, get_service_name
from google_apis import forms

action_words = ['create', 'delete', 'add', 'insert', 'remove', 'select', 'update'] # Add and Insert technically perform the same operation, but neither are technically included in the other's synonyms list
questions = {
    'textQuestion': ['text question', 'short question', 'long question', 'paragraph question'],
    'scaleQuestion': ['scale question', 'linear scale question'],
    'dateQuestion': ['date question'],
    'timeQuestion': ['time question'],
    'choiceQuestion': ['choice question', 'check box question', 'radio question', 'drop down question']
}
choices = {
    'option': ['choice', 'option', 'check box', 'drop down', 'radio']
}
simplified_attributes = {
    'paragraph': ['paragraph'],
    'shuffle': ['shuffle'],
    'type': ['type', 'choice type'],
    'includeYear': ['include year'],
    'includeTime': ['include time'],
    'duration': ['duration'],
    'low': ['low', 'low limit'],
    'high': ['high', 'high limit'],
    'lowLabel': ['low label'],
    'highLabel': ['high label'],
    'required': ['required']
}

def get_action(action):
    if action is None: # If no action word was spoken by the user
        return {'ACTION': None}
    synonyms = []
    for word in wordnet.synsets(action): # Gather the list of possible synonyms from WordNet for the action word defined
        synonyms.extend(word.lemma_names())
    synonyms = list(set(synonyms)) # Make each synonym in the list unique
    print(synonyms)
    isAction = set([action]).intersection(synonyms) # Intersect and find if it is a matching action word with anyone
    global action_words
    if not isAction:
        raise Exception("No action was specified for the operation.")
    return list(isAction)[0]

def get_question_type(question):
    global questions
    for question_type in questions.keys(): # In all of the possible question types
        if question in questions[question_type]: # Check if the question spoken by the user exists
            return question_type # If so, return the question type
    return None # If not found, return None

def perform(entities):
    service_name = get_service_name()
    if service_name is None:
        if entities.get('SERVICE'):
            get_service(entities.get('SERVICE'))
        else:
            raise Exception("No service was specified for initial creation.")
    if service_name.__eq__('forms'):
        perform_forms(entities)
    pass

def perform_forms(entities):
    global choices
    operation = entities.get('ACTION')
    if operation.__eq__('create'): # Create a new document (forms, sheets)
        global service_name
        service = entities.get('SERVICE')
        if service:
            return forms.create_form(entities.get('VALUE'))
        raise Exception("Please specify what document you wish to create.")
    elif operation.__eq__('delete'): # Delete a document (forms, sheets)
        service = entities.get('SERVICE')
        if service:
            return forms.delete_form(entities.get('VALUE'))
        raise Exception("Please specify what document you wish to delete.")
    elif operation.__eq__('add') or operation.__eq__('insert'): # Add/Insert a question of specified kind OR an attribute
        question = entities.get('QUESTION')
        attribute = entities.get('ATTRIBUTE')
        if question:
            question_type = get_question_type(question)
            if question_type:
                extra_info = None
                if question_type.__eq__('textQuestion'):
                    if not question.find('long') or not question.find('paragraph'):
                        extra_info = True
                    else:
                        extra_info = False
                elif question_type.__eq__('choiceQuestion'):
                    if not question.find('check box'):
                        extra_info = 'CHECKBOX'
                    elif not question.find('drop down'):
                        extra_info = 'DROP_DOWN'
                    else:
                        extra_info = "RADIO"
                return forms.create_question(question_type, entities.get('VALUE'), extra_info)
            raise Exception("No question of the type '" + question + "' exists.")
        elif attribute:
            for optionText in choices['option']:
                if not optionText.find(attribute):
                    return forms.get_option(entities.get('VALUE'), 'add')
            raise Exception("You did not specify what to " + operation + " in the question.")
        raise Exception("You did not specify what to " + operation + " or specified an incorrect item.")
    elif operation.__eq__('remove'): # Remove the specified question or attribute (for choice only)
        attribute = entities.get('ATTRIBUTE')
        question = entities.get('QUESTION')
        if attribute:
            for optionText in choices['option']:
                if not optionText.find(attribute):
                    return forms.get_option(entities.get('VALUE'), 'remove')
            raise Exception("You did not specify what to remove in the question.")
        elif question:
            return forms.delete_question(entities.get('VALUE'))
        raise Exception("You did not specify what to remove or specified an incorrect item.")
    elif operation.__eq__('select'): # Select either a form or a question to edit currently
        question = entities.get('QUESTION')
        service = entities.get('SERVICE')
        if question:
            return forms.select_question(entities.get('VALUE'))
        elif service:
            return forms.select_form(entities.get('VALUE'))
    elif operation.__eq__('update'): # Update the attributes inside a question
        attribute = entities.get('ATTRIBUTE')
        if attribute:
            global simplified_attributes
            for key in simplified_attributes.keys():
                attributes = simplified_attributes[key]
                for attr in attributes:
                    if attr.__eq__(attribute):
                        return forms.update_attribute(key, entities.get('VALUE'))
            raise Exception("No attribute named '" + attribute + "' exists.")
        raise Exception("No attribute was given to update.")
    raise Exception("No action word was identified.")
