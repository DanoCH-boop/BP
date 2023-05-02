import librosa
from misc.convert import convert

def get_wav(file, canvas_height):

    wav_filename = convert(file, 800)

    # Load the audio file using librosa
    y, sr = librosa.load(wav_filename, sr=None)
    # Calculate the x and y coordinates of the waveform lines
    num_frames = y.size
    y_scale = canvas_height / 2
    y_coords = (y[:-1] + y[1:]) * y_scale * 2
    print("convert", num_frames)
    return y_coords, sr
