
def process_sub(sub, index_len):
    """Processes a subtitle to a column format"""
    num_time_first = ' ' * index_len + '   '.join(str(sub).split('\n')[:3])
    sub_width = len(num_time_first) - len(sub.text.split("\n", 1)[0])
    other_lines = [' ' * sub_width + line for line in str(sub).splitlines()[3:]]
    processed_sub = num_time_first + '\n' + '\n'.join(other_lines)
    if processed_sub[-1] != "\n":
        processed_sub += "\n"
    processed_sub += "\n"

    return processed_sub