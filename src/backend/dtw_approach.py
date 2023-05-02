import librosa
from fastdtw import fastdtw
import numpy as np


def dtw_appr(file1, file2, amp=0.25):
    # Load .wav files using librosa
    x, sr1 = librosa.load(file1, sr=None)
    y, sr2 = librosa.load(file2, sr=None)

    if sr1 != sr2:
        print("\033[91m" + f"sr1 ({sr1}Hz) and sr2 ({sr2}Hz) are not the same"  + "\033[0m")
        exit(1)

    # Divide the signal into frames of 10ms each
    frame_length = int(sr1*amp)  
    
    frames1 = librosa.util.frame(x, frame_length=frame_length, axis=0, hop_length=frame_length)
    frames2 = librosa.util.frame(y, frame_length=frame_length, axis=0, hop_length=frame_length)
    print("frames done")

    # Normalize each frame and create a NumPy array
    # nema vplyv na vysledok ak pouzijem librosa.util.normalize
    normalized_frames1 = np.array([librosa.util.normalize(frame) for frame in frames1])
    normalized_frames2 = np.array([librosa.util.normalize(frame) for frame in frames2])
    print("normalistation done")

    # Calculate MFCCs for each frame and create a NumPy array
    mfccs1 = np.array([librosa.feature.mfcc(y=frame, sr=sr1, n_mfcc=10) for frame in normalized_frames1])
    mfccs2 = np.array([librosa.feature.mfcc(y=frame, sr=sr1, n_mfcc=10) for frame in normalized_frames2])

    # Reshape to a more logical shape (x, 10, 10) -> (x, 100), gives different results
    mfccs1 = mfccs1.reshape(mfccs1.shape[0],mfccs1.shape[1]*mfccs1.shape[2])
    mfccs2 = mfccs2.reshape(mfccs2.shape[0],mfccs2.shape[1]*mfccs2.shape[2])
    print("mfccs done")

    # Perform DTW using the fastdtw algorithm, using radius=10, which is optimal balance between speed and accuracy
    # according to the paper
    # distance is not important in our case
    _, path = fastdtw(mfccs1, mfccs2, radius=10)
    print("dtw done")

    return path

if __name__ == "__main__":
    from find_cuts import find_cuts
    file1 = "C:/Users/pewdi/Desktop/BP/example/example_8khz.wav"
    file2 = "C:/Users/pewdi/Desktop/BP/example/example_trim_8khz.wav"
    path = dtw_appr(file1, file2)
    cuts = 0.25*find_cuts(path)
    print(cuts)
             
