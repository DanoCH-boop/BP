import os
import librosa
import numpy as np

def convert(filename, canvas_width, canvas_height, mm=None, mode=None):
    wav_filename = filename.rsplit('.', 1)[0] + "_8khz.wav"
    mp4_to_wav1 = f"ffmpeg -i {filename} -ar 8000 -y {wav_filename}"
    # mp4_to_wav2 = f"ffmpeg -i {args[1]} -ar 8000 {args[1].split('.', 1)[0]}.wav"
    os.system(mp4_to_wav1)
    print("Conversion done")
    # os.system(mp4_to_wav2)
 
    # Load the audio file using librosa
    y, sr = librosa.load(wav_filename, sr=None)
    print(mode)
    if mm != None:
        if mode == "Kept":
            for start, end in mm:
                s = int(start*sr)
                e = int(end*sr)
                y[s:e] = 0.0
        elif mode == "Removed":
            prv_end = 0
            for start, end in mm:
                s = int(start*sr)
                e = int(end*sr)
                y[prv_end:s] = 0.0
                prv_end = e
            y[prv_end:] = 0.0
        # for mode "both" it stays the same

    # Calculate the x and y coordinates of the waveform lines
    num_frames = y.size
    x_scale = canvas_width / num_frames
    y_scale = canvas_height / 2
    x_coords = np.arange(num_frames - 1) * x_scale
    y_coords = (y[:-1] + y[1:]) / 2 * y_scale

    return x_coords, y_coords, sr
