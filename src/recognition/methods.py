import os
import json
import wave
import zipfile
import rarfile
from pydub import AudioSegment, effects
from vosk import Model, KaldiRecognizer
from recognition.settings import UPLOADED_FILES_PATH, RECOGNITION_FILES_PATH, ARCHIVED_FILES_PATH, MODELS_FILES_PATH


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


def stereo_to_mono(file):
    stereo_sound = AudioSegment.from_mp3(file)
    mono_sounds = stereo_sound.split_to_mono()
    output_path_left = os.path.splitext(file)[0] + "_left.mp3"
    output_path_right = os.path.splitext(file)[0] + "_right.mp3"
    mono_sounds[0].export(output_path_left, format="mp3")
    mono_sounds[1].export(output_path_right, format="mp3")
    return [output_path_left, output_path_right]


def stereo_to_mono_wav(file):
    stereo_sound = AudioSegment.from_wav(file)
    mono_sounds = stereo_sound.split_to_mono()
    output_path_left = os.path.splitext(file)[0] + "_left.wav"
    output_path_right = os.path.splitext(file)[0] + "_right.wav"
    mono_sounds[0].export(output_path_left, format="wav")
    mono_sounds[1].export(output_path_right, format="wav")
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


def normalize(input_file, path, media_type):
    if media_type == "mp3":
        sound = AudioSegment.from_mp3(path+input_file)
        print("Старая dBFS: ", sound.dBFS, "\n")
        sound_after = effects.normalize(sound)
        #sound_after = sound.apply_gain(+20)
        output_path_norm = RECOGNITION_FILES_PATH + os.path.splitext(input_file)[0] + "_norm.mp3"
        sound_after.export(output_path_norm, format="mp3")
        print("Новая dBFS: ", sound_after.dBFS, "\n")
        return output_path_norm
    elif media_type == "wav":
        sound = AudioSegment.from_wav(path + input_file)
        print("Старая dBFS: ", sound.dBFS, "\n")
        sound_after = effects.normalize(sound)
        #sound_after = sound.apply_gain(+20)
        output_path_norm = RECOGNITION_FILES_PATH + os.path.splitext(input_file)[0] + "_norm.wav"
        sound_after.export(output_path_norm, format="wav")
        print("Новая dBFS: ", sound_after.dBFS, "\n")
        return output_path_norm


def transcript_file(input_file, model_path, model):
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


def zipfiles(path, first_input_file, normalize_flag, file_name):
    if not os.path.exists(ARCHIVED_FILES_PATH+os.path.splitext(file_name)[0]):
        os.mkdir(ARCHIVED_FILES_PATH+os.path.splitext(file_name)[0])
    zip_file = zipfile.ZipFile(f'{ARCHIVED_FILES_PATH+os.path.splitext(file_name)[0]}/{os.path.splitext(first_input_file)[0]}_{int(normalize_flag)}.zip','w')
    with zip_file as zf:
        for folderName, subFolders, files in os.walk(path):
            for file in files:
                if file.startswith(os.path.splitext(first_input_file)[0]):
                    # create complete filepath of file in directory
                    file_path = os.path.join(folderName, file)
                    # Add file to zip
                    zf.write(file_path, os.path.basename(file_path))
    return zip_file.filename


def save_all_zip(path, fname, normalize_flag, file_name):

    zip_file = zipfile.ZipFile(f'{path}/{os.path.splitext(file_name)[0]}_{int(normalize_flag)}.zip', 'a')
    with zip_file as zf:
        for folderName, subFolders, files in os.walk(path):
            for file in files:
                if file.startswith(f'{os.path.splitext(fname)[0]}'):
                    # create complete filepath of file in directory
                    file_path = os.path.join(folderName, file)
                    # Add file to zip
                    zf.write(file_path, os.path.basename(file_path))
    return zip_file.filename


def unrar_files(archive):
    with rarfile.RarFile(archive, 'r') as rar_file:
        rar_file.extractall(os.path.splitext(archive)[0])


def mp3_parse(normalize_flag, file_name, media_type, model):
    normalize_audio = []
    monofiles = []
    if normalize_flag:
        normalize_audio = normalize(file_name, UPLOADED_FILES_PATH, media_type)
    if media_type == "mp3" and normalize_flag:
        monofiles = stereo_to_mono(normalize_audio)
    elif media_type == "mp3" and not normalize_flag:
        monofiles = stereo_to_mono(UPLOADED_FILES_PATH + file_name)
    wave_mono_files = []
    for file in monofiles:
        wave_mono_files.append(mp3_to_wav(file))
    for file in wave_mono_files:
        trancription = transcript_file(file, MODELS_FILES_PATH, model)
        json_to_file(trancription[0], trancription[1])


def wav_parse(file_name, media_type, model, format_type):
    if media_type == "wav" and not format_type:
        trancription = transcript_file(UPLOADED_FILES_PATH+file_name, MODELS_FILES_PATH, model)
        json_to_file(trancription[0], trancription[1])
    else:
        raise Exception
