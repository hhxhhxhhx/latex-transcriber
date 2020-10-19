
def replace(lines):
    start_align = None
    index = 0
    while index < len(lines):
        lower_case = lines[index].lower()
        start_align = _align_helper(lower_case, lines, index, 'left', 'flushleft', start_align)
        start_align = _align_helper(lower_case, lines, index, 'right', 'flushright', start_align)
        start_align = _align_helper(lower_case, lines, index, 'center', 'center', start_align)
        if lower_case.startswith('..align justify'):
            if start_align:
                lines[index] = '\\end{{{0}}}'.format(start_align)
            else:
                lines.pop(index)
            start_align = None
        index += 1

    return lines, start_align

def _align_helper(lower_case, lines, i, word, second_word, start_align):
    if lower_case.startswith('..align ' + word):
        if start_align:
            lines[i] = '\\end{{{0}}}'.format(start_align)
        lines.insert(i+1, '')
        lines.insert(i+2, '\\begin{' + second_word + '}')
        if not start_align:
            lines.pop(i)
        start_align = second_word
    return start_align
