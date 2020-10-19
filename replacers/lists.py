def replace(lines):
    nested_list_total = 0 # Used to indent
    nested_list_names = []
    for i in range(len(lines)):
        if nested_list_total and lines[i].strip().startswith('.. '): # Each item to begin with ".. "
            lines[i] = '    '*nested_list_total + '\\item ' + lines[i].strip()[3:]
        elif lines[i].strip().startswith('..begin list'):
            if len(lines[i].strip()) > 12 and lines[i].strip()[13:].strip() == 'bullet': # Bullet point lists don't have numbering
                lines[i] = '    '*nested_list_total + '\\begin{{{0}}}'.format('itemize')
                nested_list_names.append('itemize')
            elif len(lines[i].strip()) > 12 and lines[i].strip()[13:].strip().find('bullet') != -1: # Stuff after the 'bullet' are the optional labels
                label_type = lines[i][lines[i].find('bullet') + 6:].strip()
                lines[i] = '    '*nested_list_total + '\\begin{{{0}}}[label={1}]'.format('itemize', label_type)
                nested_list_names.append('itemize')
            elif len(lines[i].strip()) <= 12: # If the entire line is '..begin list'
                lines[i] = '    '*nested_list_total + '\\begin{{{0}}}'.format('enumerate')
                nested_list_names.append('enumerate')
            else: # If there is something after '..begin list' and it's not 'bullet', that's also a label
                label_type = lines[i].strip()[12:].strip()
                label_type = label_type.replace('a', '\\alph*') # Use 'a' to represent the alphabet
                label_type = label_type.replace('i', '\\roman*') # Use 'i' to use roman numerals
                label_type = label_type.replace('1', '\\arabic*') # Use '1' to use arabic numerals
                lines[i] = '    '*nested_list_total + '\\begin{{{0}}}[label={1}]'.format('enumerate', label_type)
                nested_list_names.append('enumerate')
            nested_list_total += 1
        elif lines[i].strip().startswith('..end list'):
            nested_list_total -= 1
            lines[i] = '    '*nested_list_total + '\\end{{{0}}}'.format(nested_list_names.pop())
        elif nested_list_total and not lines[i].strip().startswith('.. '):
            lines[i] = '    '*nested_list_total + lines[i].strip()
    return lines
