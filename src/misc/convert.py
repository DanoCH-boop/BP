import os

def convert(filename, sr):
    abr = "_8khz.wav"
    if sr == 800:
        abr = "_800hz.wav"
    wav_filename = filename.rsplit('.', 1)[0] + abr
    mp4_to_wav1 = f"ffmpeg -i {filename} -ar {str(sr)}  -y {wav_filename}"
    os.system(mp4_to_wav1)
    print("Conversion done")

    return wav_filename

