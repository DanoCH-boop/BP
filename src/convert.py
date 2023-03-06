import os
import librosa
import numpy as np

def convert(filename, canvas_width, canvas_height):
    wav_filename = filename.rsplit('.', 1)[0] + ".wav"
    mp4_to_wav1 = f"ffmpeg -i {filename} -ar 8000 -y {wav_filename}"
    # mp4_to_wav2 = f"ffmpeg -i {args[1]} -ar 8000 {args[1].split('.', 1)[0]}.wav"
    os.system(mp4_to_wav1)
    print("Conversion done")
    # os.system(mp4_to_wav2)
 
    # Load the audio file using librosa
    y, _ = librosa.load(wav_filename, sr=None)

    # Calculate the x and y coordinates of the waveform lines
    num_frames = y.size
    x_scale = canvas_width / num_frames
    y_scale = canvas_height / 2
    x_coords = np.arange(num_frames - 1) * x_scale
    y_coords = (y[:-1] + y[1:]) / 2 * y_scale

    return x_coords, y_coords



