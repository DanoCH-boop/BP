import pysrt
import sys
from convert import convert
from align import align
from openfiles import openfiles

if __name__ == "__main__":
    
    # Example run: python sub_aligner.py first.wav second.wav first.srt second.srt
    args = sys.argv[1:]
    print(args)
    
    # if(len(args) == 0):
    #     filenames = openfiles()

    if(len(args) == 0):
        args = list(["Lotr_RotK_1.mp4", "Lotr_RotK_2.mp4",
                    "meet2.srt", "meet2_try3.srt"])
    
    convert(args)
    # align(args)

    # subs = pysrt.open(args[3])
    # for sub in subs:
    #     print(sub)

    print("END")
