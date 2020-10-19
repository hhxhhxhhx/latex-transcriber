
def replace(lines, find_index):
    _beginproof = find_index(lines, '..begin proof')
    while _beginproof != -1:
        if lines[_beginproof][lines[_beginproof].index('..begin proof') + 13:].strip():
            lines[_beginproof] = lines[_beginproof][:lines[_beginproof].index('..begin proof')] + \
                                    '\\begin{{{0}}}[Proof {1}]'.format('proof', lines[_beginproof][lines[_beginproof].index('..begin proof') + 13:].strip())
        else:
            lines[_beginproof] = lines[_beginproof][:lines[_beginproof].index('..begin proof')] + '\\begin{proof}'
        _beginproof = find_index(lines, '..begin proof')

    _endproof = find_index(lines, '..end proof')
    while _endproof != -1:
        lines[_endproof] = lines[_endproof][:lines[_endproof].index('..end proof')] + '\\end{proof}'
        _endproof = find_index(lines, '..end proof')

    return lines
