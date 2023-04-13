import whisper

model = None

def load_model(modelType = 'base.en'):
    global model
    if model is None:
        model = whisper.load_model(modelType, download_root="speech_model/")
    return model

def speech_to_text():
    global model
    model = load_model()
    result = model.transcribe("output.wav")
    print("Generated Text: " + result['text'])
    return result['text'].lower()