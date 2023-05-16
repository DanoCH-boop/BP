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

    if len(subs) == 0:
        return -1, -2, start, end
    
    # DEV
    # if (mode):
    #     shift = end - start

    # part1 = subs.slice(starts_before={'minutes': start / 60})
    # part2 = subs.slice(starts_after={'minutes': end / 60})
    # part2.shift(seconds=shift)
    # DEV

    part1 = subs.slice(starts_before={'seconds': start})
    part2 = subs.slice(ends_after={'seconds': end})

    # cut is inside a subtitle
    if len(part1) != 0 and len(part2) != 0:
        if part1[-1] == part2[0]:
            start_index = end_index = part1[-1].index
            part2.shift(seconds=shift)
            del(part1[-1])
            del(part2[0])
            shifted_subs = part1 + part2
            shifted_subs.save(out_srtfile)
            return start_index, end_index, start, end
            
    part2.shift(seconds=shift)

    start_index = subs[0].index
    end_index = subs[-1].index
    print(start_index, end_index)
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

        # if the part which is not in cut is too small
        if start - time_convert(part1[-1].start) < 1 :
            start_index = part1[-1].index
            del(part1[-1]) 

    
    print(start_index, end_index)
    if len(part2) != 0:
        end_index = part2[0].index - 1
        print(start_index, end_index)
        problem_time2 = time_convert(part2[0].start)
        # cut ends after a subtitle starts, we compare against start, since part2 is already shifted
        if problem_time2 < start:
            off = start - problem_time2
            dur = time_convert(part2[0].duration)
            delta = off / dur
            part2[0].start += {'seconds': off}
            part2[0].text = part2[0].text[int(delta * len(part2[0].text)) - 1:]

        # if the part which is not in cut is too small
        if time_convert(part2[0].end) - start < 1 :
            end_index = part2[0].index
            del(part2[0]) 

    shifted_subs = part1 + part2

    print("Start End:", start+offset, end+offset)
    print("Subtitles to remove", start_index, end_index)
        
    # Save the edited subtitles
    shifted_subs.save(out_srtfile)

    return start_index, end_index, start, end
