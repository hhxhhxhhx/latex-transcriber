
def replace(lines, find_index):
    for i in range(5):
        _beginsection = find_index(lines, '..begin {0}section'.format('sub' * i))
        while _beginsection != -1:
            text = lines[_beginsection][len('..begin {0}section'.format('sub' * i)) + 1:].strip()
            if text.startswith('nonum'):
                lines[_beginsection] = '\\{0}section*{{{1}}}'.format('sub' * i, text[6:])
            else:
                lines[_beginsection] = '\\{0}section{{{1}}}'.format('sub' * i, text)
            _beginsection = find_index(lines, '..begin {0}section'.format('sub' * i))
    return lines
