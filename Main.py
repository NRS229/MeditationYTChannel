import random
import os
import ffmpeg
from pydub import AudioSegment


def translate_structure(structure_path):
    # Variables
    blocks_path = "Blocks/"
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
            output += groups[random.randint(0, len(groups)-1)]
            groups = []
        # Group start
        elif line == "[\n":
            in_group = True
        # Group finish
        elif line == "]\n":
            in_group = False
            group_number += 1
        # If it's a file
        elif line.startswith("└ ") or line.startswith("~ "):
            # If there's a minimum time
            if "*" in line:
                pos = line.index("*")
                min_time = line[pos - 1: pos + 3]
                line = line.replace(min_time, "")
            else:
                min_time = ""
            # If it repeats (X3)
            if "X" in line:
                times = line.split("X")[1]
                file = line[2:-4]
            # If it does no repeats
            else:
                times = 1
                file = line[2:-1]
            # Translate the line the number of times asked
            for _ in range(int(times)):
                # If the line is part of a group
                if in_group:
                    if len(groups) <= group_number:
                        groups.append(blocks_path + folder + file + "/" + min_time + "\n")
                    else:
                        groups[group_number] += blocks_path + folder + file + "/" + min_time + "\n"
                # If the line is not part of a group
                else:
                    # If it is silence (~)
                    if "~" in line:
                        output += line
                    else:
                        output += blocks_path + folder + file + "/" + min_time + "\n"
    # Close the file
    f.close()
    # Return the result as a list
    return output.split("\n")[:-1]


def merge_audio_files(input_files, output_name):
    output_file = "Output/" + output_name + ".wav"
    output = AudioSegment.empty()
    for file in input_files:
        # If there's a silence
        if "~" in file:
            # Create silence audio segment
            time = file.split("~ ")[1]
            silent_segment = AudioSegment.silent(duration=(1000 * int(time)))
            output += silent_segment
        else:
            # If there's a minimum time
            if "*" in file:
                pos = file.index("*")
                min_time = file[pos - 1: pos + 3]
                file = file.replace(min_time, "")
                min_time = min_time.split("*")[1]
            else:
                min_time = 0
            # Read wav file to an audio segment
            audio = AudioSegment.from_wav(file)
            # Add silence if the file takes less than the min_time
            if int(min_time) > audio.duration_seconds:
                # Create silence audio segment
                silent_segment = AudioSegment.silent(duration=(1000 * (int(min_time) - audio.duration_seconds)))
                audio = audio + silent_segment
            # Add audio to output
            output += audio
    # Export the final output
    output.export(output_file, format="wav")


def create_audio_paths():
    audio_paths = []
    for line in translate_structure("Structure.txt"):
        # If it is silence (~)
        if "~" in line:
            audio_paths.append(line)
        else:
            # If there's a minimum time
            if "*" in line:
                pos = line.index("*")
                min_time = line[pos - 1: pos + 3]
                line = line.replace(min_time, "")
            else:
                min_time = ""
            wav_file = line + random.choice(os.listdir(line))
            while (wav_file in audio_paths) or (".DS_Store" in wav_file):
                wav_file = line + random.choice(os.listdir(line))
            else:
                audio_paths.append(wav_file + min_time)
    return audio_paths


def create_video(image_path, audio_path):
    input_still = ffmpeg.input(image_path)
    input_audio = ffmpeg.input(audio_path)
    (
        ffmpeg
            .concat(input_still, input_audio, v=1, a=1)
            .output("Output/output.mp4")
            .run(overwrite_output=True)
    )


# Run the methods
merge_audio_files(create_audio_paths(), "audio")
create_video("Input/image.jpg", "Output/audio.wav")
