# Google Talk

We present to you Google Talk, the open source extension designed to automate Google Applications (such as Documents, Forms, Slides, Sheets, and so on). The entire system is designed to run by introducing a central server which will receive instructions from one or multiple users using the extension, and process on the audio input by converting the speech to text, extracting useful information from the text, and performing the operation requested by the user.

# Project Description

Google Talk is a Chromium-based extension that provides accessibility options to the physically abled and beginners by providing a voice assistant that will allow them to perform various tasks on viable Google Applications - and for this solution, we aim for Google Forms and Google Sheets primarily (Sheets have not been implemented yet). The project uses Natural Language Processing and Deep Learning methodologies to eliminate rule-based approach to performing the tasks. These tasks can be creating a new form, adding new questions, changing the format of a certain text, etc., using voice commands.

The user can record their command as voice input, which is recorded and sent from the extension to the server. There, the server picks the audio file to convert it into text format, and the text is deciphered to extract relevant and desired information. This information is further used to determine the legibility of the command and either perform the operation by communicating with the Google APIs if the command is understood or inform the user the command is insufficient/invalid if the command is not understood. In this manner, the user doesn’t need to have prior knowledge to use the certain Google Application to perform the specific task.

# Prerequisites

Please follow this before you proceed with the "How to run" section:
1. Create a Service Account Key on your Google Cloud Platform: (https://console.cloud.google.com/apis/dashboard).
2. Make sure that the Google Forms and Google Drive APIs are enabled in your project.
3. Download the service account key as a JSON file and place it in the **google_apis** folder by the name of "service_account_credentials.json" 

# How to run

Follow these guidelines to ensure a smooth launch to the Chrome extension:
1. Ensure that you extract the contents of the files and folders exclusively in a folder (you can name it anything).
2. Create a folder called "speech_model" and place the speech model folder inside it, and name that folder "model-medium".
    2.1. We used the VOSK English model with Dynamic Graph (Link: https://alphacephei.com/vosk/), but you can change the code to include any other speech model you prefer.
3. Create another folder called "ner_model" and place the NER model folder inside it, and name that folder "model-last" (base model is from Spacy, using 'en_web_core_lg' module, trained on a custom dataset of ours).
4. Open up Chrome (or any other Chromium-based browser) and navigate to the Extensions settings.
5. There should be a "Developer Mode" tab. Enable it.
6. Click on "Load unpacked" and select the folder in which you extracted the files and folder to load the extension up.
7. Use the "requirements.txt" to install the required libraries on Python.
8. Either open up the folder in VSCode, or any other suitable IDE, or navigate to the folder in the terminal, and execute the python script by the name of "server.py".
9. Ensure that the server has launched correctly (you should get a "* Debugger is active!" prompt on the terminal).

Now speak away in the Chrome Extension!
