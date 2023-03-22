import librosa
from fastdtw import fastdtw
import numpy as np


def normalize(x):
    new = x - np.mean(x)
    new = new / np.abs(new).max()
    return new

# Load .wav file using librosa
x, sr1 = librosa.load('../example/example.wav', sr=None) # 5s cut od 10s do 15s a 5s cut od 30 do 35s
y, sr2 = librosa.load('../example/example_trim.wav', sr=None) # tu chyba tych 5s+5s=10s

if sr1 != sr2:
    print("sr1 and sr2 are not the same")

# Divide the signal into frames of 10ms each
frame_length = int(sr1*0.1)  # 100ms = 0.1s, poskytlo lepsi vysledok [(150,50), (352,50)] pri 48kHz a [(150,50), (354,50)] pri 8kHz
#frame_length = int(sr1*0.01) # 10ms = 0.01s, horsi vysledok

# FUNKCIA KTORU STE MI POSKYTLI MA ROVNAKY VYSLEDOK AKO librosa.util.frame

# window = frame_length
# shift = frame_length
# shape = ((x.shape[0] - window) // shift + 1, window) + x.shape[1:]
# strides = (x.strides[0]*shift,x.strides[0]) + x.strides[1:]
# frames1 = np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)

frames1 = librosa.util.frame(x, frame_length=frame_length, axis=0, hop_length=frame_length)
frames2 = librosa.util.frame(y, frame_length=frame_length, axis=0, hop_length=frame_length)
print("frames done")

# Normalize each frame and create a NumPy array
# nema vplyv na vysledok ak pouzijem librosa.util.normalize
normalized_frames1 = np.array([normalize(frame) for frame in frames1])
normalized_frames2 = np.array([normalize(frame) for frame in frames2])
print("normalistation done")

# Calculate MFCCs for each frame and create a NumPy array
mfccs1 = np.array([librosa.feature.mfcc(y=frame, sr=sr1, n_mfcc=10) for frame in normalized_frames1])
mfccs2 = np.array([librosa.feature.mfcc(y=frame, sr=sr1, n_mfcc=10) for frame in normalized_frames2])
print("mfccs done")

# DTW
distance, path = fastdtw(mfccs1, mfccs2, radius=1) # radius=1 stacil pri 48khz, pri 8khz treba radius=2
print("dtw done")

# HLADANIE STRIHOV - pravdepobone velmi zly pristup

path = np.array(path)
diffs = np.diff(path[:, 1])

# tymto najdem cas/frame kedy sa signaly prestavaju rovnat
change_indices = np.where(diffs != 1)[0] + 1
print(change_indices)

# tymto kodom som chcel eliminovat useky vo vnutri "strihu", kde sa pri dtw aj tak namapovali 3 prvky po sebe "presne"
# tj v "path" ako "[(150,100), (151,100), (152,100),--> (153,101), (154,102), (155,103) <--, (156,103), (157,103), (158,103)]"
#                                                       ^          tento usek         ^
diffs2 = np.diff(change_indices) 
real_change = np.where(diffs2 > 3)[0] + 1 # 3 sedelo pri 100ms framoch, pri 10ms trebalo dat tak 20
print(real_change)

# tymto splitnem/odlisim rozne strihy od seba
result = np.split(change_indices, real_change)
indexes_of_change = [(indexes[-1], indexes.size) for indexes in result]
print(indexes_of_change)
# indexes_of_change obsahuje indexy framov kde konci strih a aky dlhy je
# stale si robim ten isty problem v podstate, ze porovnavam prvok po prvku
