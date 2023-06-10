import subprocess
import mlflow.spacy

subprocess.call(["python", "-m", "spacy", "init", "config", "config.cfg", "--lang", "en", "--pipeline", "ner", "--optimize", "accuracy", "--force"])
subprocess.call(["python", "-m", "spacy", "train", "config.cfg", "--output", "./model/", "--paths.train", "./training_data.spacy", "--paths.dev", "./validation_data.spacy"])

nlp_ner = spacy.load(os.getcwd() + "/model/model-last")

mlflow.spacy.save_model(nlp_ner, "./mlflow_artifacts/")
