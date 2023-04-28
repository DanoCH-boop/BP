import numpy as np
import librosa
import pysrt
from backend.sub_edit import sub_edit
from scipy import signal as sig
import os


def align(args):
    # Load signals
    # signal1, sr1 = librosa.load(args[0], sr=8000, res_type='linear')
    print("HERE", args, "HERE")
    wav_filename1 = args[0].rsplit('.', 1)[0] + "_8khz.wav"
    wav_filename2 = args[1].rsplit('.', 1)[0] + "_8khz.wav"

    mp4_to_wav1 = f"ffmpeg -i {args[0]} -ar 48000  -y {wav_filename1}"
    mp4_to_wav2 = f"ffmpeg -i {args[1]} -ar 48000 -y {wav_filename2}"
    os.system(mp4_to_wav1)
    os.system(mp4_to_wav2)
    signal1, sr1 = librosa.load(r"C:\Users\pewdi\Desktop\BP\media\night_of_the_living_dead_512kbtest.wav", sr=None)
    signal2, sr2 = librosa.load(r"C:\Users\pewdi\Desktop\BP\media\night_of_the_living_dead_512kb_midRemovedtest.wav",
                                sr=None)

    # Copy subs to new .srt file
    subs = pysrt.open(args[2])
    out_srtfile = args[1].rsplit('.', 1)[0] + ".srt"
    subs.save(out_srtfile)

    mode = 0
    # Decide what signal is longer
    if signal1.size - signal2.size < 0:
        signal1, signal2 = signal2, signal1
        mode = 1

    # Find the first mismatch
    pr = signal1[:signal2.size] == signal2
    first_mismatch = np.argwhere(pr == False)[0] if (np.argwhere(pr == False).size != 0) else signal2.size

    last1 = int(first_mismatch)
    last2 = int(first_mismatch)

    offset = 0.0
    indexes = []
    mismatches = []

    # Signals differ at the end
    # |||||||||||||||||||||||||
    # ||||||||||||||||
    if last2 == signal2.size:
        s, e, start, end = sub_edit(last1 / sr1, signal1.size / sr1, args, mode, offset)
        indexes.append((s, e))
        mismatches.append((start, end))
        exit()

    # Main loop
    while True:
        # snip = signal2[last2:(last2+48000)]
        print("Last:", last1, last2)
        c = sig.correlate(signal1[last1:], signal2[last2:], mode='valid', method='fft')
        maxarg = int(np.argmax(c))
        print("Peak", maxarg / sr1)
        peak = int(maxarg) + last1
        print("Peak + last1:", peak / sr1)
        # mismatches.append((last1/sr1, peak/sr1))
        s, e, start, end = sub_edit(last1 / sr1, peak / sr1, args, mode, offset)
        offset += maxarg / sr1
        last1 = int(peak)

        cmp_arr = signal1[last1:(last1 + signal2.size - last2)] == signal2[last2:]
        mismatch = np.argwhere(cmp_arr == False)[0] if (np.argwhere(cmp_arr == False).size != 0) else -1

        if s <= e:
            indexes.append((s, e))
            mismatches.append(start)

        if mismatch == -1:
            break
        print("Mismatch:", type(mismatch), mismatch / sr1)

        last1 += int(mismatch)
        last2 += int(mismatch)

    removed_indexes = []
    grouped_ri = []
    for index in indexes:
        aggr = []
        for i in range(index[0], index[1] + 1):
            removed_indexes.append(i)
            aggr.append(i)
        grouped_ri.append(aggr)

    indexes = np.array(removed_indexes, dtype=int)
    grouped_ri = np.array(grouped_ri, dtype=int)
    print(indexes, mismatches, grouped_ri)

    return indexes, mismatches, grouped_ri
