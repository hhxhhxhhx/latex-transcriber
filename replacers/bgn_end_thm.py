
def replace(lines, find_index):
    _begintheorem = find_index(lines, '..begin thm')
    while _begintheorem != -1:
        text = lines[_begintheorem][12:].split()
        if len(text) == 1:
            lines[_begintheorem] = '\\begin{{{0}}}'.format(text[0][0].upper() + text[0][1:])
        else:
            lines[_begintheorem] = '\\begin{{{0}}}[{1}]'.format(text[0][0].upper() + text[0][1:], " ".join(text[1:]))
        _begintheorem = find_index(lines, '..begin thm')

    _endtheorem = find_index(lines, '..end thm')
    while _endtheorem != -1:
        text = lines[_endtheorem][10:].split()
        lines[_endtheorem] = '\\end{{{0}}}'.format(text[0][0].upper() + text[0][1:])
        _endtheorem = find_index(lines, '..end thm')
    return lines
