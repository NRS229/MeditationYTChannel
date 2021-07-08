# -*- coding: utf-8 -*-
import random
import os
import ffmpeg
import datetime
import subprocess
from pydub import AudioSegment, effects
from Google import Create_Service
from googleapiclient.http import MediaFileUpload

#Global variables
structure_path          = "Structure.txt"
background_music_path   = "Input/backgroundMusic.mp3"
background_video_path   = "Input/backgroundVideo.mov"
generated_voice_path    = "Output/generatedVoice.wav"
video_to_upload_path    = "Output/output.mp4"
thumbnail_image_path    = "Input/thumbnail.jpg"
video_title             = "10 minute Guided Meditation - First"
video_category_number   = 22 # People & Blogs
video_description       = "Take a moment and let this guided meditation help you relax"
video_tags              = ['Meditation', 'Mindfulness', 'Relax', 'Stress', 'De-stress', 'Calm', 'Meditate', 'Float']
video_made_for_kids     = False
video_notify_subscribers= False


def get_structure_without_groups(structure_path):
    # Variables
    blocks_path = "Input/Blocks/"
    folder = ""
    output = ""
    groups = []
    group_number = 0
    in_group = False

    f = open(structure_path, "r")
    lines = f.readlines()
    for line in lines:
        # If it's a folder
        if line.endswith("/\n"):
            folder = line[:-1]
        # Groups section finish
        elif line == ")\n":
            output += groups[random.randint(0, len(groups) - 1)]
            groups = []
        # Group start
        elif line == "[\n":
            in_group = True
        # Group finish
        elif line == "]\n":
            in_group = False
            group_number += 1
        # If it's a file
        elif line.startswith("└ "):
            file = line[2:-1]
            # If the line is part of a group
            if in_group:
                if len(groups) <= group_number:
                    groups.append(blocks_path + folder + file + "\n")
                else:
                    groups[group_number] += blocks_path + folder + file + "\n"
            # If the line is not part of a group
            else:
                output += blocks_path + folder + file + "\n"
    # Close the file
    f.close()
    # Return the result as a list
    return output.split("\n")[:-1]


def get_paths_from_structure(structure_array):
    output = []
    for line in structure_array:
        if " " in line:
            output.append(line.split(" ")[0])
        else:
            output.append(line)
    return output


def get_repetitions(structure_array):
    output = []
    for line in structure_array:
        if "*" in line:
            # repetition is between "*" and " "
            output.append(int((line.split("*"))[1].split(" ")[0]))
        else:
            output.append(1)
    return output


def get_silences_after_audio(structure_array, repetitions):
    output = []
    for i in range(len(structure_array)):
        for rep in range(repetitions[i]):
            if "~" in structure_array[i]:
                # silence after audio is between "~" and " "
                output.append(int((structure_array[i].split("~"))[1].split(" ")[0]))
            else:
                output.append(0)
    return output


def get_minimum_times(structure_array, repetitions):
    output = []
    for i in range(len(structure_array)):
        for rep in range(repetitions[i]):
            if "%" in structure_array[i]:
                # minimum time is between "%" and " "
                output.append(int((structure_array[i].split("%"))[1].split(" ")[0]))
            else:
                output.append(0)
    return output


def get_paths_with_random_audio_files(paths_array, repetitions):
    output = []
    for i in range(len(paths_array)):
        for rep in range(repetitions[i]):
            wav_file = paths_array[i] + "/" + random.choice(os.listdir(paths_array[i]))
            while (wav_file in output) or (".DS_Store" in wav_file):
                wav_file = paths_array[i] + "/" + random.choice(os.listdir(paths_array[i]))
            output.append(wav_file)
    return output


def merge_audio_files(paths, minimum_times, silences):
    output = AudioSegment.empty()
    for i in range(len(paths)):
        audio = AudioSegment.from_wav(paths[i])
        # if there's a minimum time
        if int(minimum_times[i]) > audio.duration_seconds:
            # the line was cut because PyCharm asked nicely :)
            silence_for_minimum_time = \
                AudioSegment.silent(duration=(1000 * (int(minimum_times[i]) - audio.duration_seconds)))
            audio += silence_for_minimum_time
            # if there's a silence after
            silence_after = AudioSegment.silent(duration=(1000 * (int(silences[i]))))
            audio += silence_after
        output += audio
    # Normalize the audio
    normalized_output = effects.normalize(output)
    # Export the final output
    return normalized_output


def add_background_music(audio, output_path, music_path):
    music = AudioSegment.from_file(music_path, format="mp3")
    music = (music - 5).fade_in(10000).fade_out(10000)
    overlay = audio.overlay(music, position=0)
    overlay.export(output_path, format="wav")


def create_video(video_path, audio_path, output_path):
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)
    command = 'ffmpeg  -stream_loop -1 -i ' + video_path + ' -i ' +  audio_path + ' -shortest -map 0:v:0 -map 1:a:0 -y ' + output_path
    subprocess.Popen(command.split()).wait()

    # ( ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path).run(overwrite_output=True) )


def upload_youtube(video_path, thumbnail_path):
    CLIENT_SECRET_FILE = 'SecretFiles/client_secret.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    upload_date_time = datetime.datetime(2021, 6, 25, 12, 30, 0).isoformat() + '.000Z'

    request_body = {
        'snippet': {
            'categoryId': video_category_number,
            'title': video_title,
            'description': video_description,
            'tags': video_tags
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': upload_date_time,
            'selfDeclaredMadeForKids': video_made_for_kids,
        },
        'notifySubscribers': video_notify_subscribers
    }

    mediaFile = MediaFileUpload(video_path)

    response_upload = service.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()

    service.thumbnails().set(
        videoId=response_upload.get('id'),
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()


def main():
    structure_without_groups = get_structure_without_groups(structure_path)
    paths = get_paths_from_structure(structure_without_groups)
    repetitions = get_repetitions(structure_without_groups)
    silences_after_audio = get_silences_after_audio(structure_without_groups, repetitions)
    minimum_times = get_minimum_times(structure_without_groups, repetitions)
    paths_with_random_audio_files = get_paths_with_random_audio_files(paths, repetitions)

    # Create and save the main audio
    audio = merge_audio_files(paths_with_random_audio_files, minimum_times, silences_after_audio)
    # Add background music
    add_background_music(audio, generated_voice_path, background_music_path)
    # Generate the video
    create_video(background_video_path, generated_voice_path, video_to_upload_path)

    # Upload to youtube
    upload_youtube(video_to_upload_path, thumbnail_image_path)


if __name__ == "__main__":
    main()
