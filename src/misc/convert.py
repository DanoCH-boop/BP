import os
import librosa
import numpy as np


def convert(filename, canvas_height):
    wav_filename = filename.rsplit('.', 1)[0] + "_8khz.wav"
    mp4_to_wav1 = f"ffmpeg -i {filename} -ar 800  -y {wav_filename}"
    # mp4_to_wav2 = f"ffmpeg -i {args[1]} -ar 8000 {args[1].split('.', 1)[0]}.wav"
    os.system(mp4_to_wav1)
    print("Conversion done")
    # os.system(mp4_to_wav2)

    # Load the audio file using librosa
    y, sr = librosa.load(wav_filename, sr=None)
   
    # Calculate the x and y coordinates of the waveform lines
    num_frames = y.size
    print(num_frames)
    # x_scale = 600 / num_frames
    y_scale = canvas_height / 2
    # x_coords = np.arange(num_frames - 1) / 10
    y_coords = (y[:-1] + y[1:]) * y_scale * 2
    print("convert", num_frames)
    return y_coords, sr
