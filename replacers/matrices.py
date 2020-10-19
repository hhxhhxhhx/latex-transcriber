
def replace(lines):
    within_matrix = False
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..begin matrix'):
            within_matrix = True
            lines[index] = '$\\begin{bmatrix}'
        elif lines[index].startswith('..end matrix'):
            within_matrix = False
            if lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                lines[index - 1] = lines[index - 1][:-2]
            lines[index] = '\\end{bmatrix}$'
        elif within_matrix and not lines[index].strip():
            lines.pop(index)
            continue
        elif within_matrix: # Automatically changes spaces to be breaks between items
            while lines[index].find('  ') != -1: # Get rid of double spaces
                lines[index].replace('  ', ' ')
            lines[index] = lines[index].strip() # Remove newline characters at the end
            if lines[index].endswith('\\\\'):
                lines[index] = lines[index][:-2].strip()
            elif lines[index].endswith('\\nl'):
                lines[index] = lines[index][:-3].strip()
            lines[index] = lines[index].replace(' ', ' & ') # Replace spaces with ' & '
            lines[index] += ' \\\\' # Re-add newline characters after each line
        index += 1
    return lines