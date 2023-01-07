IMPORTANT:
Follow these guidelines to ensure a smooth launch to the Chrome extension:
1. Ensure that you extract the contents of the files and folders exclusively in a folder (you can name it anything).
2. Create a folder called "speech_model" and place the speech model folder inside it, and name that folder "model-medium".
    2.1. I used the VOSK English model, but you can change the code to include any other speech model.
3. Create another folder called "ner_model" and place the NER model folder inside it, and name that folder "model-last".
4. Open up Chrome (or any other Chromium-based browser), and navigate to the Extensions settings.
5. There should be a "Developer Mode" tab. Enable it.
6. Click on "Load unpacked" and select the folder in which you extracted the files and folder to load the extension up.
7. Use the "requirements.txt" to install the required libraries on Python.
8. Either open up the folder in VSCode, or any other suitable IDE, or navigate to the folder in the terminal, and execute a python script by the name of "server.py".
9. Ensure that the server has launched correctly (you should get a "* Debugger is active!" prompt on the terminal).

Now speak away in the Chrome Extension!