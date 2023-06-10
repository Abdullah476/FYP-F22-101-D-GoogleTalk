import subprocess

try:
    import spacy
except ImportError:
    subprocess.call(["python", "-m", "pip", "install", "spacy-streamlit>=1.0.0"])
    import spacy

from spacy.tokens import DocBin
from tqdm import tqdm
from spacy import displacy
import json
import os

if not spacy.util.is_package("en"):
    subprocess.call(["python", "-m", "spacy", "download", "en"])
    
if not spacy.util.is_package("en_core_web_lg"):
    subprocess.call(["python", "-m", "spacy", "download", "en_core_web_lg"])

nlp = spacy.blank("en") # Load a new SpaCy model (by default, it loads the "en_core_web_lg" library which is more expansive and accurate but storage-costly)
db = DocBin() # Create a DocBin object for storing the trained model

fTrain = open("annotationsTrain.json", encoding="utf-8")
train_data = json.load(fTrain)
fTrain.close()
for text, annot in tqdm(train_data['annotations']):
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot['entities']:
        span = doc.char_span(start, end, label=label, alignment_mode='contract')
        if span is None:
            print("Skipping entry")
        else:
            ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("./training_data.spacy") # Save the DocBin object

fVal = open("annotationsVal.json", encoding="utf-8")
val_data = json.load(fVal)
fTrain.close()
for text, annot in tqdm(val_data['annotations']):
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot['entities']:
        span = doc.char_span(start, end, label=label, alignment_mode='contract')
        if span is None:
            print("Skipping entry")
        else:
            ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("./validation_data.spacy") # Save the DocBin object
