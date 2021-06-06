import random
import os
import ffmpeg
from pydub import AudioSegment


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


def get_paths_with_random_audio_files(paths_array, repetitions):
    output = []
    for i in range(len(paths_array)):
        for rep in range(repetitions[i]):
            wav_file = paths_array[i] + "/" + random.choice(os.listdir(paths_array[i]))
            while (wav_file in output) or (".DS_Store" in wav_file):
                wav_file = paths_array[i] + "/" + random.choice(os.listdir(paths_array[i]))
            output.append(wav_file)
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


def get_repetitions(structure_array):
    output = []
    for line in structure_array:
        if "*" in line:
            # repetition is between "*" and " "
            output.append(int((line.split("*"))[1].split(" ")[0]))
        else:
            output.append(1)
    return output


def merge_audio_files(output_name, paths, minimum_times, silences):
    output_file = "Output/" + output_name + ".wav"
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
    # Export the final output
    output.export(output_file, format="wav")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def create_video(image_path, audio_path):
    input_still = ffmpeg.input(image_path)
    input_audio = ffmpeg.input(audio_path)
    (
        ffmpeg
        .concat(input_still, input_audio, v=1, a=1)
        .output("Output/output.mp4")
        .run(overwrite_output=True)
    )


def main():
    structure_path = "Structure.txt"
    structure_without_groups = get_structure_without_groups(structure_path)
    paths = get_paths_from_structure(structure_without_groups)
    repetitions = get_repetitions(structure_without_groups)
    silences_after_audio = get_silences_after_audio(structure_without_groups, repetitions)
    minimum_times = get_minimum_times(structure_without_groups, repetitions)
    paths_with_random_audio_files = get_paths_with_random_audio_files(paths, repetitions)

    # export as .wav file
    merge_audio_files("audio", paths_with_random_audio_files, minimum_times, silences_after_audio)


if __name__ == "__main__":
    main()