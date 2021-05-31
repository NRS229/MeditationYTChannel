import random


def translate_structure(structure_path):
    # Variables
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
                        groups.append(folder + file + ".txt\n")
                    else:
                        groups[group_number] += folder + file + ".txt\n"
                # If the line is not part of a group
                else:
                    output += folder + file + ".txt\n"
    # Close the file
    f.close()
    # Return the result as a list
    return output.split("\n")[:-1]


def create_script():
    return_lines = []
    f = ""
    for line in translate_structure("Structure.txt"):
        # Open the file and save the shuffled lines in a variable
        f = open("Blocks/" + line, "r")
        lines = f.readlines()
        # Add an unique line
        random.shuffle(lines)
        while lines[0] in return_lines:
            random.shuffle(lines)
        else:
            return_lines.append(lines[0])
    # Close the file
    f.close()
    # Return the result
    return return_lines


# Run the methods
print("---------------- SAVE SCRIPT TO FILE ----------------")
f = open("Output/script.txt", "w+")
for line in create_script():
    f.write(line)
f.close()
