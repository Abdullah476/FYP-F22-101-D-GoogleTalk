from nltk.corpus import wordnet
from google_apis.shared import get_service, get_service_name
from google_apis import forms, sheets
from word2number import w2n
import re

action_words = ['create', 'delete', 'add', 'insert', 'remove', 'select', 'update', 'write', 'clear', 'protect', 'merge', 'unmerge', 'copy', 'paste', 'show', 'submit', 'enter'] # Add and Insert technically perform the same operation, but neither are technically included in the other's synonyms list
questions = {
    'textQuestion': ['text question', 'short question', 'long question', 'paragraph question'],
    'scaleQuestion': ['scale question', 'linear scale question'],
    'dateQuestion': ['date question'],
    'timeQuestion': ['time question'],
    'choiceQuestion': ['choice question', 'check box question', 'checkbox question', 'radio question', 'drop down question', 'dropdown question']
}
choices = {
    'option': ['choice', 'option', 'check box', 'drop down', 'radio', 'checkbox', 'dropdown']
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

def range_converter(_range):
    _range = forms.text_literal(_range)
    # Remove all whitespaces
    _range = "".join(_range.split())
    # Now find the middle part of the string and append : to it. We do that by splitting the components clearly
    _range = re.split(r'(\d+)', _range)
    _range.remove('')
    # Finally, insert that : and construct the string
    _range.insert(2, ':')
    return "".join(_range)

def get_action(action):
    if action is None: # If no action word was spoken by the user
        return None
    synonyms = []
    for word in wordnet.synsets(action): # Gather the list of possible synonyms from WordNet for the action word defined
        synonyms.extend(word.lemma_names())
    synonyms = list(set(synonyms)) # Make each synonym in the list unique
    global action_words # Preprocessing to extract definitive action word properly
    for action_word in action_words:
        if action_word != action.lower() and action_word in synonyms:
            synonyms.remove(action_word)
    isAction = set([action.lower()]).intersection(synonyms) # Intersect and find if it is a matching action word with anyone
    if len(synonyms) == 0 and action in action_words:
        return action
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
    get_service(entities.get('SERVICE'))
    service_name = get_service_name()
    if service_name.__eq__('forms'):
        perform_forms(entities)
    elif service_name.__eq__('sheets'):
        perform_sheets(entities)
    pass

def perform_forms(entities):
    global choices
    operation = entities.get('ACTION')
    if operation.__eq__('create'): # Create a new document (forms, sheets)
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
        position = entities.get('POSITION')
        # print(position, entities.get('INDEX'))
        if entities.get('INDEX') is None:
            index = None
        else:
            index = w2n.word_to_num(entities.get('INDEX'))

        if position is not None:
            if position.lower() == "after":
                if index is None:
                    index = 0
                index += 1
            elif position.lower() == "before":
                if index is None:
                    index = 0
                if index != 0:
                    index -= 1


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
                    if not question.find('check'):
                        extra_info = 'CHECKBOX'
                    elif not question.find('drop'):
                        extra_info = 'DROP_DOWN'
                    else:
                        extra_info = "RADIO"
                return forms.create_question(question_type, entities.get('VALUE'), extra_info, index)
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
        raise Exception("Either the form or question you are trying to select does not exist.")
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
    elif operation.__eq__('show'): # Show answers filled out in the form
        return forms.show_answers()

    elif operation.__eq__('enter'): # Enter an answer into the selected or specified question
        return forms.enter_answer(entities.get('VALUE'), entities.get('QUESTION'))

    elif operation.__eq__('submit'): # Submit the form using POST operation
        return forms.submit_form()

    raise Exception("No action word was identified.")

def perform_sheets(entities):
    print("I am in the sheets")
    global choices
    operation = entities.get('ACTION')
    if operation.__eq__('create'):
        service = entities.get('SERVICE')
        if service:
            return sheets.create_spreadsheet(entities.get('VALUE'))
        raise Exception("Please specify what document you wish to create.")
    elif operation.__eq__('delete'):
        service = entities.get('SERVICE')
        if service:
            return sheets.delete_spreadsheet(entities.get('VALUE'))
        raise Exception("Please specify what document you wish to delete.")
    elif operation.__eq__('add') or operation.__eq__('insert') or operation.__eq__('write'):
        _range = entities.get('RANGE')
        if _range:
            # One work is going to be done here: get the range and format it in A1 or R1C1 notation before using it.
            # A1 / R1C1 notations: https://developers.google.com/sheets/api/guides/concepts#cell
            _range = range_converter(_range)
            return sheets.write_to_spreadsheet(_range, entities.get('VALUE'))
        raise Exception("Please specify in which range you wish to" + operation + ".")
    elif operation.__eq__('clear') or operation.__eq__('remove'):
        _range = entities.get('RANGE')
        if _range:
            _range = range_converter(_range)
            return sheets.clear_from_spreadsheet(_range)
        raise Exception("Please specify the range from which you wish to remove values.")
    elif operation.__eq__('protect'):
        _range = entities.get('RANGE')
        if _range:
            _range = range_converter(_range)
            return sheets.protect_range(_range)
        raise Exception("Please specify the range to protect.")
    elif operation.__eq__('merge') or operation.__eq__('unmerge'):
        _range = entities.get('RANGE')
        if _range:
            _range = range_converter(_range)
            if operation.__eq__('unmerge'):
                return sheets.merge_range(_range, False)
            return sheets.merge_range(_range)
        raise Exception("Please specify the range to protect.")
    elif operation.__eq__('select'):
        service = entities.get('SERVICE')
        if service:
            return sheets.select_sheet(entities.get('VALUE'))
        raise Exception("The sheet you are trying to select does not exist.")
    raise Exception("No action word was identified.")