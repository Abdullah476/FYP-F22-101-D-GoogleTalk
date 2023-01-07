import os, subprocess, wave, audioop

def is_ffmpeg():
    from shutil import which
    return which('ffmpeg') is not None

def WEBM_TO_WAV():
    if not is_ffmpeg():
        os.remove('output.webm')
        raise Exception("FFMPEG is not installed on your system.")
    # Convert WEBM to WAV mono for our speech recognition model
    command = ['ffmpeg', '-i', 'output.webm', '-vn', '-ar', '16000', '-ac', '1', '-loglevel', 'quiet', 'output.wav']
    subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    os.remove('output.webm')