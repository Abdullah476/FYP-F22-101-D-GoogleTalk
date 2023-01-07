from spacy import load, displacy

# The code to the model training can be followed here:
# https://colab.research.google.com/drive/1zBKPY1saVoHl_cnfoAo3dUzE08sNXqjm

model = None

def load_model(modelType="last"):
    global model
    if model is None:
        model = load(r'.\\ner_model\\model-' + modelType)
    return model

def ner_interpretation(text):
    global model
    model = load_model()
    interpretation = model(text) # Simply pass the string text into the model to get the result
    entities = interpretation.ents # Extract the entities from it
    if entities is None: # If the NER model failed to pick any annotations from the string, return None
        raise Exception("No command was said.")
    return dict(zip([entity.label_ for entity in entities], [entity.text for entity in entities]))
    # Else, return the labels and their corresponding text in a dictionary format by:
    # - Using list comprehension to create two lists, one for labels, and one for text
    # - Zipping them together (as, common sense would have it, both lists would be equal in size, so there will be zero issues)
    # - Calling the built-in 'dict' function to convert the zipped file to a dictionary