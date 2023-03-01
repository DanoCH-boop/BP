import pysrt

def sub_edit(start, end, args, mode, offset):
    # Load the subtitles from the .srt file
    subs = pysrt.open(args[3]) 
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
    
    # Save the edited subtitles
    shifted_subs.save(args[3])
    