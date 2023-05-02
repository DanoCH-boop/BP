import pysrt
from misc.time_convert import time_convert


def sub_edit(start, end, out_srtfile, offset, mode=0):
    """Edits the subtitles to fit the cut"""
    # Load the subtitles from the .srt file
    subs = pysrt.open(out_srtfile)

    # Edit the subtitles
    end -= offset
    start -= offset
    shift = start - end

    if (mode):
        shift = end - start

    # part1 = subs.slice(starts_before={'minutes': start / 60})
    # part2 = subs.slice(starts_after={'minutes': end / 60})
    # part2.shift(seconds=shift)
    part1 = subs.slice(starts_before={'minutes': start/60})
    part2 = subs.slice(ends_after={'minutes': end/60})
    inside = 0

    # cut is inside a subtitle
    if len(part1) != 0 and len(part2) != 0:
        if part1[-1] == part2[0]:
            inside = 1
            h = part1[-1].start.hours
            min = part1[-1].start.minutes
            sec = part1[-1].start.seconds
            ms = part1[-1].start.milliseconds
            s = pysrt.SubRipTime(h, min, sec, ms)
            e = pysrt.SubRipTime(seconds=end)
            text = str(part1[-1].text)
            item = pysrt.SubRipItem(0, s, e, text)

    part2.shift(seconds=shift)

    if inside == 1:
        part1[-1] = item

    start_index = -1
    end_index = -2
    if len(part1) != 0:
        start_index = part1[-1].index + 1
        # editing the subtitles that overlap with cut
        problem_time1 = time_convert(part1[-1].end)

        # cut starts before a subtitle ends
        if problem_time1 > start:
            off = problem_time1 - start
            dur = time_convert(part1[-1].duration)
            delta = 1 - off / dur
            part1[-1].end += {'seconds': -off}
            part1[-1].text = part1[-1].text[:int(delta * len(part1[-1].text)) + 1]

    shifted_subs = part1 + part2

    print("Start End:", start, end)

    if len(part2) != 0:
        end_index = part2[0].index - 1

        problem_time2 = time_convert(part2[0].start)
        # cut ends after a subtitle starts
        if problem_time2 < start:
            off = start - problem_time2
            dur = time_convert(part2[0].duration)
            delta = off / dur
            print(delta)
            part2[0].start += {'seconds': off}
            part2[0].text = part2[0].text[int(delta * len(part2[0].text)) - 1:]

    print("Subtitles to remove", start_index, end_index)

    shifted_subs.clean_indexes()

    if inside == 1:
        start_index = -1
        end_index = -2
        
    # Save the edited subtitles
    shifted_subs.save(out_srtfile)

    return start_index, end_index, start, end
