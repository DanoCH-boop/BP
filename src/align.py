import numpy as np
import librosa
import pysrt
from sub_edit import sub_edit
from scipy import signal as sig

def align(args):

    # Load signals
    # signal1, sr1 = librosa.load(args[0], sr=8000, res_type='linear')
    signal1, sr1 = librosa.load(f"{args[0].rsplit('.', 1)[0]}.wav", sr=None)
    signal2, _ = librosa.load(f"{args[1].rsplit('.', 1)[0]}.wav", sr=sr1)
    
    # Copy subs to new .srt file
    subs = pysrt.open(args[2])
    out_srtfile = args[1].rsplit('.', 1)[0] + ".srt"
    subs.save(out_srtfile)

    mode = 0
    # Decide what signal is longer
    if(signal1.size - signal2.size < 0):
        signal1, signal2 = signal2, signal1
        mode = 1

    # Find the first mismatch
    pr = signal1[:signal2.size] == signal2
    first_mismatch = np.argwhere(pr==False)[0] if(np.argwhere(pr==False).size != 0) else signal2.size

    last1 = int(first_mismatch)
    last2 = int(first_mismatch)

    offset = 0.0
    indexes = []
    mismatches = []

    # Signals differ at the end
    # |||||||||||||||||||||||||
    # ||||||||||||||||
    if(last2 == signal2.size):
        s, e, start, end = sub_edit(last1/sr1, signal1.size/sr1, args, mode, offset)
        indexes.append((s,e))
        mismatches.append((start,end))
        exit()

    # Main loop
    while(True):
        # snip = signal2[last2:(last2+48000)]
        print("Last:",last1,last2)
        c = sig.correlate(signal1[last1:], signal2[last2:], mode='valid', method='fft')
        print("Peak", np.argmax(c)/sr1)
        peak = int(np.argmax(c)) + last1
        print("Peak + last1:", peak/sr1)

        s, e, start, end = sub_edit(last1/sr1, peak/sr1, args, mode, offset)
        offset += np.argmax(c)/sr1
        last1 = int(peak)

        cmp_arr = signal1[last1:(last1+signal2.size-last2)] == signal2[last2:]
        mismatch = np.argwhere(cmp_arr==False)[0] if(np.argwhere(cmp_arr==False).size != 0) else -1

        if s <= e:
            indexes.append((s,e))
        mismatches.append((start,end))

        if(mismatch == -1):
            break
        print("Mismatch:", type(mismatch),mismatch/sr1)

        last1 += int(mismatch)
        last2 += int(mismatch)
        
    return indexes, mismatches
