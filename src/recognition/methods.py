import os
from datetime import datetime
from pydub import AudioSegment

from .settings import *
import json
import wave
import time
from vosk import Model, KaldiRecognizer


# Save file to uploads folder
async def save_file_to_uploads(file, filename):
    with open(f'{UPLOADED_FILES_PATH}{filename}', "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()


# Format filename
def format_filename(file, file_id=None, name=None):
    # Split filename and extention
    filename, ext = os.path.splitext(file.filename)

    # Rename file
    if name is None:
        filename = str(file_id)
    else:
        filename = name

    return filename + ext


def stereo_to_mono(file,path):
    stereo_sound = AudioSegment.from_mp3(path+file)
    mono_sounds = stereo_sound.split_to_mono()
    output_path_left = RECOGNITION_FILES_PATH + os.path.splitext(file)[0] + "_left.mp3"
    output_path_right = RECOGNITION_FILES_PATH + os.path.splitext(file)[0] + "_right.mp3"
    mono_sounds[0].export(output_path_left, format="mp3")
    mono_sounds[1].export(output_path_right, format="mp3")

    return [output_path_left, output_path_right]


def mp3_to_wav(file, skip=0, excerpt=False):
    sound = AudioSegment.from_mp3(file)  # load source
    sound = sound.set_channels(1)  # mono
    sound = sound.set_frame_rate(16000)  # 16000Hz

    if excerpt:
        excrept = sound[skip * 1000:skip * 1000 + 30000]  # 30 seconds - Does not work anymore when using skip
        output_path = os.path.splitext(file)[0] + "_excerpt.wav"
        excrept.export(output_path, format="wav")
    else:
        audio = sound[skip * 1000:]
        output_path = os.path.splitext(file)[0] + ".wav"
        audio.export(output_path, format="wav")

    return output_path

def transcript_file(input_file, model_path):
    # Check if file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(os.path.basename(input_file) + " not found")

        # Check if model path exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(os.path.basename(model_path) + " not found")

    # open audio file
    wf = wave.open(input_file, "rb")

    # check if wave file has the right properties
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise TypeError("Audio file must be WAV format mono PCM.")

    # Initialize model
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    # To store our results
    jresult = []
    while True:
        data = wf.readframes(4000)  # use buffer of 4000
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            # Convert json output to dict
            result_dict = json.loads(rec.Result())

            # Extract text values and append them to transcription list
            jresult.append(result_dict)

    wf.close()  # close audiofile
    return jresult, input_file



def json_to_file(jresult, input_file):
    with open(f'{os.path.splitext(input_file)[0]}.json', 'w', encoding='utf-8') as file:
        json.dump(jresult, file, ensure_ascii=False, indent=4)
    return f'{os.path.splitext(input_file)[0]}.json'

import zipfile

def zipfiles(path,first_input_file):
    zip_file = zipfile.ZipFile(f'{ARCHIVED_FILES_PATH}{os.path.splitext(first_input_file)[0]}.zip', 'w')
    with zip_file as zf:
        for folderName, subfolders, files in os.walk(path):
            for file in files:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, file)
                # Add file to zip
                zf.write(filePath, os.path.basename(filePath))
    return zip_file.filename