
def replace(lines):
    within_table = False
    table_name = None
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..begin table math'):
            table_name = "array"
            within_table = True
            lines[index] = '$\\begin{{{0}}}{{{1}}}'.format(table_name, lines[index][18:].strip())
        elif lines[index].startswith('..begin table'):
            table_name = "tabular"
            within_table = True
            lines[index] = '\\begin{{{0}}}{{{1}}}'.format(table_name, lines[index][13:].strip())
        elif lines[index].startswith('..end table'):
            within_table = False
            if lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                lines[index - 1] = lines[index - 1][:-2]
            lines[index] = '\\end{{{0}}}{1}'.format(table_name, ('$' if table_name == 'array' else ''))
        elif within_table and not lines[index].strip():
            lines.pop(index)
            continue
        elif within_table: # Automatically changes "\ " to be breaks between items
            lines[index] = lines[index].strip() # Remove newline characters at the end
            if lines[index].startswith('\\hline'):
                index += 1
                continue
            if lines[index].endswith('\\\\'):
                lines[index] = lines[index][:-2].strip()
            elif lines[index].endswith('\\nl'):
                lines[index] = lines[index][:-3].strip()
            lines[index] = lines[index].replace('\\ ', '& ') # Replace delimiters with ' & '
            if lines[index].endswith('\\'):
                lines[index] = lines[index][:-1] + '&'
            lines[index] += ' \\\\' # Re-add newline characters after each line
        index += 1
    return lines
