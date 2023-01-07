import sys

sys.dont_write_bytecode = True

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import os
from webmToWav import WEBM_TO_WAV
from speechToText import speech_to_text, load_model as load_speech_model
from textToEntities import ner_interpretation, load_model as load_ner_model
from deriveActions import get_action, perform
from traceback import print_exc

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-type'
CORS(app)

@app.route('/email', methods = ['POST'])
@cross_origin(origin='*', headers='*')
def get_id():
    json = request.get_json()
    print(json)
    return {'response': "Email received"}

@app.route('/receive', methods = ['POST', 'OPTIONS'])
@cross_origin(origin='*', headers='*')
def get_file():
    try:
        file = request.files.get('audio') # Get the audio Blob
        file.save(file.filename) # Save it with the requested file name from Javascript Fetch
        WEBM_TO_WAV() # Convert the file to WAV (most, if not all, Speech Recognition libraries work seamlessly with .wav files)
        stt = speech_to_text() # Read the WAV file and extract speech from it
        os.remove('output.wav') # Remove the WAV file as it is no longer required
        entities = ner_interpretation(stt) # Pass the text to the NER model for information extraction
        entities['ACTION'] = get_action(entities.get('ACTION')) # Pass the action word (if found by the NER model) to get the appropriate action word
        # Continue from here
        perform(entities) # Send the entities now to evaluate and perform the operation desired by the user
        response = jsonify("Operation executed successfully.") # If the operation was done, produce a JSON that confirms the operation performed successfully.
        response.headers.add('Access-Control-Allow-Origin', '*') # Allow ACAO 
        return response # Return the response to the user
    except Exception as e:
        print_exc() # Print out the error for debugging purposes
        response = jsonify(str(e)) # Also, send the error to the user for information
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/', methods=['GET', 'POST'])
def home(name=None):
    return render_template("popup.html", name=name)

if __name__ == "__main__":
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getcwd() + "\\google_apis\\service_account_credentials.json"
    load_speech_model()
    load_ner_model()
    app.run(host="127.0.0.1", port=8080, debug=True)