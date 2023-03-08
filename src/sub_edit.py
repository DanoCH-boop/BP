import pysrt
import linecache

def sub_edit(start, end, args, mode, offset):
    # Load the subtitles from the .srt file
    out_srtfile = args[1].rsplit('.', 1)[0] + ".srt"
    subs = pysrt.open(out_srtfile)

    # Edit the subtitles
    end -= offset
    start -= offset
    shift = -(end-start)

    if(mode):
        shift = end-start

    part1 = subs.slice(starts_before={'minutes': start/60})
    part2 = subs.slice(starts_after={'minutes': end/60})
    part2.shift(seconds=shift)
    shifted_subs = part1 + part2

    print("Start End:", start, end)

    start_index = part1[-1].index + 1
    end_index = part2[0].index

    line_index1 = linecache.getlines(args[2]).index(str(start_index)+'\n') + 1
    line_index2 = linecache.getlines(args[2]).index(str(end_index)+'\n')
    # Save the edited subtitles
    shifted_subs.save(out_srtfile)

    return line_index1, line_index2
    