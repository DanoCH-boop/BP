
def time_convert(time):
    """Convets time from time format to seconds"""
    return time.hours*3600 +time.minutes*60 + time.seconds + time.milliseconds/1000