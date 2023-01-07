from vosk import Model, KaldiRecognizer, SetLogLevel
import wave, json

model = None

def load_model(modelType = 'medium'):
    global model
    if model is None:
        model = Model(r'.\\speech_model\\model-' + modelType)
    return model

def speech_to_text():
    SetLogLevel(-1) # For debugging purposes
    wav = wave.open('output.wav')
    arrText = []
    global model
    model = load_model() # You can also try using 'model-small' for quicker but less accurate responses'
    # 'model-medium' works best, and it handles British, American, and Indian English accents well enough (not too well - try saying 'form')
    recognizer = KaldiRecognizer(model, wav.getframerate())
    recognizer.SetWords(True)

    while True:
        data = wav.readframes(4000)
        if not data:
            break
        if recognizer.AcceptWaveform(data):
            arrText.append(json.loads(recognizer.Result()))

    arrText.append(json.loads(recognizer.FinalResult()))
    print("Generated Text: " + arrText[0]['text'])
    return arrText[0]['text']