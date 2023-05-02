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

    # part1 = subs.slice(starts_before={'minutes': start/60})
    # part2 = subs.slice(ends_after={'minutes': end/60})
    # part2.shift(seconds=shift)

    part1 = subs.slice(starts_before={'minutes': start / 60})
    part2 = subs.slice(starts_after={'minutes': end / 60})
    part2.shift(seconds=shift)
    start_index = -1
    end_index = -2
    if len(part1) != 0:
        start_index = part1[-1].index + 1
        # editing the subtitles that overlap with cut
        problem_time1 = time_convert(part1[-1].end)
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
    print("Subtitles to remove", start_index, end_index)

    # Save the edited subtitles
    shifted_subs.save(out_srtfile)

    return start_index, end_index, start, end
