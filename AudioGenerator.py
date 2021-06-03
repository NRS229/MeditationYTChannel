import random
import soundfile
import wave
import os


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
        elif line.startswith("└ "):
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
                    output += blocks_path + folder + file + "/" + min_time + "\n"
    # Close the file
    f.close()
    # Return the result as a list
    return output.split("\n")[:-1]


def merge_audio_files(input_files, output_name):
    output_file = "Output/" + output_name + ".wav"
    data = []
    for infile in input_files:
        info, samplerate = soundfile.read(infile)
        soundfile.write(infile, info, samplerate)
        w = wave.open(infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    output = wave.open(output_file, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()
    pass


def create_audio_paths():
    audio_paths = []
    for line in translate_structure("Structure.txt"):
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


# Run the methods
# merge_audio_files(create_audio_paths(), "Audio")
# print(translate_structure("Structure.txt"))
print(create_audio_paths())
