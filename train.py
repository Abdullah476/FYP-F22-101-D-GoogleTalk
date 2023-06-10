import subprocess
import mlflow.spacy
import spacy
import os

subprocess.call(["py", "-m", "spacy", "init", "config", "config.cfg", "--lang", "en", "--pipeline", "ner", "--optimize", "accuracy", "--force"])

subprocess.call(["py", "-m", "spacy", "train", "config.cfg", "--output", "./model/", "--paths.train", "./training_data.spacy", "--paths.dev", "./validation_data.spacy"])

nlp_ner = spacy.load(os.getcwd() + "/model/model-last")

mlflow.spacy.save_model(spacy_model=nlp_ner, path="./mlflow_artifacts/" + )
