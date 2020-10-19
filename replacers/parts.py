
def replace(lines):
    index = 0
    last_label = "(\\alph*)"
    resume_label = "(\\alph*)"
    using_resume = 0
    while index < len(lines):
        if lines[index].strip().startswith('p\\ '): # Each item to begin with ".. "
            lines[index] = '\\Part ' + lines[index].strip()[3:]
        elif lines[index].strip().startswith('..begin parts'):
            using_resume = 0
            if len(lines[index].strip()) <= 13 and last_label == "(\\alph*)": # If the entire line is '..begin parts'
                lines[index] = '\\begin{{{0}}}'.format('Parts')
                index += 1
                continue
                label_type = "(\\alph*)"
            else: # If there is something after '..begin parts' that's the label
                label_type = lines[index].strip()[13:].strip()
                label_type = label_type.replace('a', '\\alph*') # Use 'a' to represent the alphabet
                label_type = label_type.replace('i', '\\roman*') # Use 'i' to use roman numerals
                label_type = label_type.replace('1', '\\arabic*') # Use '1' to use arabic numerals
            if label_type == last_label:
                lines[index] = '\\begin{{{0}}}'.format('Parts')
                index += 1
                continue
            else:
                last_label = label_type
                lines[index] = "\\renewenvironment{Parts}{\n" + "\\setcounter{resumer}{0}\n" + "\\begin{enumerate}[label=" + label_type + "]\n"
                lines[index] += "\\newcommand\\Part{\\item}}{\\setcounter{resumer}{\\value{enumi}}\\end{enumerate}}"
                lines.insert(index + 1, '\\begin{{{0}}}'.format('Parts'))
                index += 1
        elif lines[index].strip().startswith('..end parts'):
            lines[index] = '\\end{{{0}}}'.format('Resume' * using_resume + 'Parts')
        elif lines[index].strip().startswith('..resume parts'):
            using_resume = 1
            if last_label == resume_label:
                lines[index] = '\\begin{{{0}}}'.format('ResumeParts')
            else:
                resume_label = last_label
                lines[index] = "\\renewenvironment{ResumeParts}{\n" + "\\begin{enumerate}[label=" + label_type + "]\n"
                lines[index] += "\\setcounter{enumi}{\\value{resumer}}\\newcommand\\Part{\\item}}{\\setcounter{resumer}{\\value{enumi}}\\end{enumerate}}"
                lines.insert(index + 1, '\\begin{{{0}}}'.format('ResumeParts'))

        index += 1
    return lines
