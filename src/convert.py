import os

def convert(args):
    mp4_to_wav1 = f"ffmpeg -i {args[0]} -acodec -ar 8000 {args[0].split('.', 1)[0]}.wav"
    mp4_to_wav2 = f"ffmpeg -i {args[1]} -ar 8000 {args[1].split('.', 1)[0]}.wav"
    os.system(mp4_to_wav1)
    os.system(mp4_to_wav2)
