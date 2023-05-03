import pysrt
import numpy as np


def get_speech_segments(file):
    """Computes the start and end of each speech segments from subtitles"""
    subs = pysrt.open(file)

    # convert the start and end times to NumPy arrays
    start_times = np.array(
        [sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000 for sub in subs])
    end_times = np.array(
        [sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000 for sub in subs])

    # combine the start and end times into a single array of speech segments
    return np.column_stack((start_times, end_times))
