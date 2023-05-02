import numpy as np
import librosa
import pysrt
from backend.sub_edit import sub_edit
from misc.convert import convert
from scipy import signal as sig
from backend.dtw_approach import dtw_appr
from backend.find_cuts import find_cuts


def align(args):
    # Load signals
    wav_file1 = convert(args[0], sr=8000)
    wav_file2 = convert(args[1], sr=8000)

    amp = 0.25

    # Copy subs to new .srt file
    subs = pysrt.open(args[2])
    out_srtfile = args[1].rsplit('.', 1)[0] + ".srt"
    subs.save(out_srtfile)

    # mode = 0
    # # Decide which signal is longer
    # if signal1.size - signal2.size < 0:
    #     signal1, signal2 = signal2, signal1
    #     mode = 1

    path = dtw_appr(wav_file1, wav_file2)

    cuts = find_cuts(path) * amp

    mismatches1 = []
    mismatches2 = []
    indexes = []
    offset = 0
    for cut in cuts:
        start = cut[0] - cut[1]
        end = cut[0]
        start_i, end_i, start_m, end_m = sub_edit(start, end, out_srtfile, offset)
        mismatches1.append((start_m + offset, end_m + offset)) 
        offset += cut[1]

        # if the cut did not remove any speech segments/subs dont append to removed_indexes
        if start_i <= end_i:
            indexes.append((start_i, end_i))
        mismatches2.append(start_m)
    
    removed_indexes = []
    grouped_ri = []
    for index in indexes:
        aggr = []
        for i in range(index[0], index[1] + 1):
            removed_indexes.append(i)
            aggr.append(i)
        grouped_ri.append(aggr)

    print(mismatches1)
    print(mismatches2)
    print(removed_indexes)
    ri = np.array(removed_indexes, dtype=int)
    grouped_ri = np.array(grouped_ri, dtype=int)

    return mismatches1, mismatches2, ri , grouped_ri
