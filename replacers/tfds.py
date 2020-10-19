
tfds_rules = ['MP', 'MT', 'DN', 'MCND', 'CNJ', 'CA', 'RAA', 'BIC', 'DIL', \
                       'DM', 'D', 'P', 'W']

def replace(lines):
    within_tfds = False
    index = 0
    line_count = 1
    expected_columns = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..begin tfds'):
            within_tfds = True
            line_count = 1
            lines[index] = '$\\begin{{{0}}}{{{1}}}'.format('array', lines[index][12:].strip())
            expected_columns = 0
            expected_columns += lines[index][12:].strip().count('c')
            expected_columns += lines[index][12:].strip().count('l')
            expected_columns += lines[index][12:].strip().count('r')
        elif lines[index].startswith('..end tfds'):
            within_tfds = False
            if lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                lines[index - 1] = lines[index - 1][:-2]
            lines[index] = '\\end{array}$'
        elif within_tfds and not lines[index].strip():
            lines.pop(index)
            continue
        elif within_tfds: # Automatically changes "\ " to be breaks between items

            # "\ " is equivalent to "&"

            lines[index] = lines[index].strip() # Remove newline characters at the end
            if lines[index].startswith('\\hline'):
                index += 1
                continue

            # Surround [] in the beginning with braces {}
            if lines[index].startswith('['):
                closing_bracket_index = lines[index].find(']')
                lines[index] = '{' + lines[index][:closing_bracket_index + 1] + '}' + lines[index][closing_bracket_index + 1:]

            # Change '[]' to be '[~]' for visual purposes
            lines[index] = lines[index].replace('[]', '[~]')

            # Remove \nl and \\ in the end
            if lines[index].endswith('\\\\'):
                lines[index] = lines[index][:-2].strip()
            elif lines[index].endswith('\\nl'):
                lines[index] = lines[index][:-3].strip()
            lines[index] = lines[index].replace('\\ ', '& ') # Replace delimiters with ' & '

            # Add line number in second position
            first_break = lines[index].find('&')
            lines[index] = lines[index][:first_break + 1] + ' ({0}) &'.format(line_count) + lines[index][first_break + 1:]

            line_count += 1
            if lines[index].endswith('\\'):
                lines[index] = lines[index][:-1] + '&'

            if lines[index].strip().endswith(' P'):
                # Check if lazy and left an extra column blank because of premise
                if lines[index].count('&') == expected_columns - 2:
                    lines[index] = lines[index][:lines[index].rindex('&') + 1] + ' &' + lines[index][lines[index].rindex('&') + 1:]
            lines[index] += ' \\\\' # Re-add newline characters after each line
            
            # MP -> \text{MP}, MT -> \text{MT}, etc. 
            lines[index] = _apply_tfds_rules_names(lines[index])
            
        index += 1
    return lines

def _apply_tfds_rules_names(line):
    for name in tfds_rules:
        line = line.replace(name, '\\text{' + name + '}')
    return line
