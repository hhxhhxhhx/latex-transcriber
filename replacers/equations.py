
def replace(lines):
    eq_type = None
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..begin eq'):
            eq_type = ('align' if 'align' in lines[index].lower() else 'gather')
            if 'number' not in lines[index].lower(): # If no numbering, add *
                eq_type += '*'
            lines[index] = '\\begin{{{0}}}'.format(eq_type)
        elif lines[index].startswith('..end eq'):
            if lines[index - 1].endswith('\\\\'):
                lines[index - 1] = lines[index - 1][:-2]
            lines[index] = '\\end{{{0}}}'.format(eq_type)
            eq_type = None
        elif eq_type and not lines[index].strip():
            lines.pop(index)
            continue
        elif eq_type and not lines[index].strip().endswith('\\\\') \
                     and not lines[index].strip().endswith('\\nl'): # Add newline character after each line break because LaTeX is dumb
            lines[index] += ' \\\\'
        index += 1
    return lines
