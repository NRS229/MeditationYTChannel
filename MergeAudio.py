import wave

fileOne = "One.wav"
fileTwo = "Two.wav"
fileThree = "Three.wav"
outputName = "MergedAudio"


def merge_audio_files(file1, file2, file3, output_name):
    infiles = ["Input/" + file1, "Input/" + file2, "Input/" + file3]
    outfile = "Output/ " + output_name + ".wav"
    data = []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

    pass


merge_audio_files(fileOne, fileTwo, fileThree, outputName)
