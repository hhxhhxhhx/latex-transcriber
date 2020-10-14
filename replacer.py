

class Replacer():

    # Set up \newtheorem and \newtheorem* commands

    def replace(self, lines, find_content, find_index):

        self.lines = lines

        """
        INITIALIZING EQUATION NUMBERING
        """
        self.equation_numbering = find_content(self.lines, '..initeq', None)

        """
        INITIALIZING THEOREMS
        """
        self.all_theorem_names = []
        _initunnumberedtheorem = find_content(self.lines, '..initheorem*', None) # Unnumbered theorems to be defined using ..initheorem*
        self.unnumbered_theorems = []
        while _initunnumberedtheorem:
            lst = _initunnumberedtheorem.split()
            # These theorems must have 1 argument: the name of the type of theorem
            if len(lst) != 1:
                print("..initheorem* requires 1 argument. Read documentation if necessary")
                exit(1)
            else:
                self.unnumbered_theorems.append(lst[0])
                self.all_theorem_names.append(lst[0])
                line_to_remove = find_index(self.lines, '..initheorem*')
                self.lines.pop(line_to_remove)
                _initunnumberedtheorem = find_content(self.lines, '..initheorem*', None)

        _initnumberedtheorem = find_content(self.lines, '..initheorem', None) # Numbered theorems to be defined using ..initheorem
        self.numbered_theorems = []
        while _initnumberedtheorem:
            lst = _initnumberedtheorem.split()
            # Must have 1 or 3 arguments: 1 if the counter is by itself
            #                             3 if the counter is subordinate or shared with something else
            if len(lst) != 1 and len(lst) != 3:
                print("..initheorem* requires exactly 2 arguments. Read documentation if necessary")
                exit(1)
            else:
                self.numbered_theorems.append(lst)
                self.all_theorem_names.append(lst[0])
                line_to_remove = find_index(self.lines, '..initheorem')
                self.lines.pop(line_to_remove)
                _initnumberedtheorem = find_content(self.lines, '..initheorem', None)

        # Check for ..begin section or ..begin subsection or ..begin subsubsection, etc. 
        # Changed default behavior from not numbering to numbering. Use ..begin section nonum to not number. 
        for i in range(5):
            _beginsection = find_index(self.lines, '..begin {0}section'.format('sub' * i))
            while _beginsection != -1:
                text = self.lines[_beginsection][len('..begin {0}section'.format('sub' * i)) + 1:].strip()
                if text.startswith('nonum'):
                    self.lines[_beginsection] = '\\{0}section*{{{1}}}'.format('sub' * i, text[6:])
                else:
                    self.lines[_beginsection] = '\\{0}section{{{1}}}'.format('sub' * i, text)
                _beginsection = find_index(self.lines, '..begin {0}section'.format('sub' * i))

        """
        COPY
        """
        self.copy_dict = {}
        copy_label = None
        copied_text = []
        index = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..begin copy'):
                if not self.lines[index][13:].strip():
                    print("..begin copy requires 1 argument. Read documentation if necessary")
                    exit(1)
                copy_label = self.lines[index][13:].strip()
                if copy_label in self.copy_dict:
                    print("Warning, copy label \"{0}\" is used multiple times. Unintended behavior may occur. The last \"..begin copy {0}\" will override all previous labels.".format(copy_label))
                self.lines.pop(index)
                continue
            elif self.lines[index].startswith('..end copy'):
                self.copy_dict[copy_label] = copied_text
                copy_label = None
                copied_text = []
                self.lines.pop(index)
                continue
            elif copy_label:
                copied_text.append(self.lines[index])
            index += 1

        """
        PASTE
        """
        index = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..paste'):
                if not self.lines[index][8:].strip():
                    print("..paste requires 1 argument. Read documentation if necessary")
                    exit(1)
                label = self.lines[index][8:].strip()
                try:
                    self.lines[index:index + 1] = self.copy_dict[label]
                    index += len(self.copy_dict[label]) - 1
                except KeyError as ke:
                    print("Copy label \"{0}\" not found!".format(label))
                    exit(1)
            index += 1

        """
        BEGIN AND END THEOREMS
        """
        _begintheorem = find_index(self.lines, '..begin thm')
        while _begintheorem != -1:
            text = self.lines[_begintheorem][12:].split()
            if len(text) == 1:
                self.lines[_begintheorem] = '\\begin{{{0}}}'.format(text[0][0].upper() + text[0][1:])
            else:
                self.lines[_begintheorem] = '\\begin{{{0}}}[{1}]'.format(text[0][0].upper() + text[0][1:], " ".join(text[1:]))
            _begintheorem = find_index(self.lines, '..begin thm')

        _endtheorem = find_index(self.lines, '..end thm')
        while _endtheorem != -1:
            text = self.lines[_endtheorem][10:].split()
            self.lines[_endtheorem] = '\\end{{{0}}}'.format(text[0][0].upper() + text[0][1:])
            _endtheorem = find_index(self.lines, '..end thm')


        """
        PROOFS
        """
        _beginproof = find_index(self.lines, '..begin proof')
        while _beginproof != -1:
            if self.lines[_beginproof][self.lines[_beginproof].index('..begin proof') + 13:].strip():
                self.lines[_beginproof] = self.lines[_beginproof][:self.lines[_beginproof].index('..begin proof')] + \
                                        '\\begin{{{0}}}[Proof {1}]'.format('proof', self.lines[_beginproof][self.lines[_beginproof].index('..begin proof') + 13:].strip())
            else:
                self.lines[_beginproof] = self.lines[_beginproof][:self.lines[_beginproof].index('..begin proof')] + '\\begin{proof}'
            _beginproof = find_index(self.lines, '..begin proof')

        _endproof = find_index(self.lines, '..end proof')
        while _endproof != -1:
            self.lines[_endproof] = self.lines[_endproof][:self.lines[_endproof].index('..end proof')] + '\\end{proof}'
            _endproof = find_index(self.lines, '..end proof')


        """
        LISTS
        """
        nested_list_total = 0 # Used to indent
        nested_list_names = []
        for i in range(len(self.lines)):
            if nested_list_total and self.lines[i].strip().startswith('.. '): # Each item to begin with ".. "
                self.lines[i] = '    '*nested_list_total + '\\item ' + self.lines[i].strip()[3:]
            elif self.lines[i].strip().startswith('..begin list'):
                if len(self.lines[i].strip()) > 12 and self.lines[i].strip()[13:].strip() == 'bullet': # Bullet point lists don't have numbering
                    self.lines[i] = '    '*nested_list_total + '\\begin{{{0}}}'.format('itemize')
                    nested_list_names.append('itemize')
                elif len(self.lines[i].strip()) > 12 and self.lines[i].strip()[13:].strip().find('bullet') != -1: # Stuff after the 'bullet' are the optional labels
                    label_type = self.lines[i][self.lines[i].find('bullet') + 6:].strip()
                    self.lines[i] = '    '*nested_list_total + '\\begin{{{0}}}[label={1}]'.format('itemize', label_type)
                    nested_list_names.append('itemize')
                elif len(self.lines[i].strip()) <= 12: # If the entire line is '..begin list'
                    self.lines[i] = '    '*nested_list_total + '\\begin{{{0}}}'.format('enumerate')
                    nested_list_names.append('enumerate')
                else: # If there is something after '..begin list' and it's not 'bullet', that's also a label
                    label_type = self.lines[i].strip()[12:].strip()
                    label_type = label_type.replace('a', '\\alph*') # Use 'a' to represent the alphabet
                    label_type = label_type.replace('i', '\\roman*') # Use 'i' to use roman numerals
                    label_type = label_type.replace('1', '\\arabic*') # Use '1' to use arabic numerals
                    self.lines[i] = '    '*nested_list_total + '\\begin{{{0}}}[label={1}]'.format('enumerate', label_type)
                    nested_list_names.append('enumerate')
                nested_list_total += 1
            elif self.lines[i].strip().startswith('..end list'):
                nested_list_total -= 1
                self.lines[i] = '    '*nested_list_total + '\\end{{{0}}}'.format(nested_list_names.pop())
            elif nested_list_total and not self.lines[i].strip().startswith('.. '):
                self.lines[i] = '    '*nested_list_total + self.lines[i].strip()

        """
        PARTS (With inspiration from CS 70's header.sty)
        """
        index = 0
        last_label = "(\\alph*)"
        resume_label = "(\\alph*)"
        using_resume = 0
        while index < len(self.lines):
            if self.lines[index].strip().startswith('p\\ '): # Each item to begin with ".. "
                self.lines[index] = '\\Part ' + self.lines[index].strip()[3:]
            elif self.lines[index].strip().startswith('..begin parts'):
                using_resume = 0
                if len(self.lines[index].strip()) <= 13 and last_label == "(\\alph*)": # If the entire line is '..begin parts'
                    self.lines[index] = '\\begin{{{0}}}'.format('Parts')
                    index += 1
                    continue
                    label_type = "(\\alph*)"
                else: # If there is something after '..begin parts' that's the label
                    label_type = self.lines[index].strip()[13:].strip()
                    label_type = label_type.replace('a', '\\alph*') # Use 'a' to represent the alphabet
                    label_type = label_type.replace('i', '\\roman*') # Use 'i' to use roman numerals
                    label_type = label_type.replace('1', '\\arabic*') # Use '1' to use arabic numerals
                if label_type == last_label:
                    self.lines[index] = '\\begin{{{0}}}'.format('Parts')
                    index += 1
                    continue
                else:
                    last_label = label_type
                    self.lines[index] = "\\renewenvironment{Parts}{\n" + "\\setcounter{resumer}{0}\n" + "\\begin{enumerate}[label=" + label_type + "]\n"
                    self.lines[index] += "\\newcommand\\Part{\\item}}{\\setcounter{resumer}{\\value{enumi}}\\end{enumerate}}"
                    self.lines.insert(index + 1, '\\begin{{{0}}}'.format('Parts'))
                    index += 1
            elif self.lines[index].strip().startswith('..end parts'):
                self.lines[index] = '\\end{{{0}}}'.format('Resume' * using_resume + 'Parts')
            elif self.lines[index].strip().startswith('..resume parts'):
                using_resume = 1
                if last_label == resume_label:
                    self.lines[index] = '\\begin{{{0}}}'.format('ResumeParts')
                else:
                    resume_label = last_label
                    self.lines[index] = "\\renewenvironment{ResumeParts}{\n" + "\\begin{enumerate}[label=" + label_type + "]\n"
                    self.lines[index] += "\\setcounter{enumi}{\\value{resumer}}\\newcommand\\Part{\\item}}{\\setcounter{resumer}{\\value{enumi}}\\end{enumerate}}"
                    self.lines.insert(index + 1, '\\begin{{{0}}}'.format('ResumeParts'))

            index += 1
        """
        EQUATIONS
        """
        eq_type = None
        index = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..begin eq'):
                eq_type = ('align' if 'align' in self.lines[index].lower() else 'gather')
                if 'number' not in self.lines[index].lower(): # If no numbering, add *
                    eq_type += '*'
                self.lines[index] = '\\begin{{{0}}}'.format(eq_type)
            elif self.lines[index].startswith('..end eq'):
                if self.lines[index - 1].endswith('\\\\'):
                    self.lines[index - 1] = self.lines[index - 1][:-2]
                self.lines[index] = '\\end{{{0}}}'.format(eq_type)
                eq_type = None
            elif eq_type and not self.lines[index].strip():
                self.lines.pop(index)
                continue
            elif eq_type and not self.lines[index].strip().endswith('\\\\') \
                         and not self.lines[index].strip().endswith('\\nl'): # Add newline character after each line break because LaTeX is dumb
                self.lines[index] += ' \\\\'
            index += 1

        """
        MATRICES
        """
        within_matrix = False
        index = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..begin matrix'):
                within_matrix = True
                self.lines[index] = '$\\begin{bmatrix}'
            elif self.lines[index].startswith('..end matrix'):
                within_matrix = False
                if self.lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                    self.lines[index - 1] = self.lines[index - 1][:-2]
                self.lines[index] = '\\end{bmatrix}$'
            elif within_matrix and not self.lines[index].strip():
                self.lines.pop(index)
                continue
            elif within_matrix: # Automatically changes spaces to be breaks between items
                while self.lines[index].find('  ') != -1: # Get rid of double spaces
                    self.lines[index].replace('  ', ' ')
                self.lines[index] = self.lines[index].strip() # Remove newline characters at the end
                if self.lines[index].endswith('\\\\'):
                    self.lines[index] = self.lines[index][:-2].strip()
                elif self.lines[index].endswith('\\nl'):
                    self.lines[index] = self.lines[index][:-3].strip()
                self.lines[index] = self.lines[index].replace(' ', ' & ') # Replace spaces with ' & '
                self.lines[index] += ' \\\\' # Re-add newline characters after each line
            index += 1

        """
        TABLES / ARRAYS
        """
        within_table = False
        table_name = None
        index = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..begin table math'):
                table_name = "array"
                within_table = True
                self.lines[index] = '$\\begin{{{0}}}{{{1}}}'.format(table_name, self.lines[index][18:].strip())
            elif self.lines[index].startswith('..begin table'):
                table_name = "tabular"
                within_table = True
                self.lines[index] = '\\begin{{{0}}}{{{1}}}'.format(table_name, self.lines[index][13:].strip())
            elif self.lines[index].startswith('..end table'):
                within_table = False
                if self.lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                    self.lines[index - 1] = self.lines[index - 1][:-2]
                self.lines[index] = '\\end{{{0}}}{1}'.format(table_name, ('$' if table_name == 'array' else ''))
            elif within_table and not self.lines[index].strip():
                self.lines.pop(index)
                continue
            elif within_table: # Automatically changes "\ " to be breaks between items
                self.lines[index] = self.lines[index].strip() # Remove newline characters at the end
                if self.lines[index].startswith('\\hline'):
                    index += 1
                    continue
                if self.lines[index].endswith('\\\\'):
                    self.lines[index] = self.lines[index][:-2].strip()
                elif self.lines[index].endswith('\\nl'):
                    self.lines[index] = self.lines[index][:-3].strip()
                self.lines[index] = self.lines[index].replace('\\ ', '& ') # Replace delimiters with ' & '
                if self.lines[index].endswith('\\'):
                    self.lines[index] = self.lines[index][:-1] + '&'
                self.lines[index] += ' \\\\' # Re-add newline characters after each line
            index += 1

        """
        TFDS
        """
        self.tfds_rules = ['MP', 'MT', 'DN', 'MCND', 'CNJ', 'CA', 'RAA', 'BIC', 'DIL', \
                           'DM', 'D', 'P', 'W']
        within_tfds = False
        index = 0
        line_count = 1
        expected_columns = 0
        while index < len(self.lines) - 1:
            if self.lines[index].startswith('..begin tfds'):
                within_tfds = True
                line_count = 1
                self.lines[index] = '$\\begin{{{0}}}{{{1}}}'.format('array', self.lines[index][12:].strip())
                expected_columns = 0
                expected_columns += self.lines[index][12:].strip().count('c')
                expected_columns += self.lines[index][12:].strip().count('l')
                expected_columns += self.lines[index][12:].strip().count('r')
            elif self.lines[index].startswith('..end tfds'):
                within_tfds = False
                if self.lines[index - 1].endswith('\\\\'): # Remove newline character at the final line
                    self.lines[index - 1] = self.lines[index - 1][:-2]
                self.lines[index] = '\\end{array}$'
            elif within_tfds and not self.lines[index].strip():
                self.lines.pop(index)
                continue
            elif within_tfds: # Automatically changes "\ " to be breaks between items

                # "\ " is equivalent to "&"

                self.lines[index] = self.lines[index].strip() # Remove newline characters at the end
                if self.lines[index].startswith('\\hline'):
                    index += 1
                    continue

                # Surround [] in the beginning with braces {}
                if self.lines[index].startswith('['):
                    closing_bracket_index = self.lines[index].find(']')
                    self.lines[index] = '{' + self.lines[index][:closing_bracket_index + 1] + '}' + self.lines[index][closing_bracket_index + 1:]

                # Change '[]' to be '[~]' for visual purposes
                self.lines[index] = self.lines[index].replace('[]', '[~]')

                # Remove \nl and \\ in the end
                if self.lines[index].endswith('\\\\'):
                    self.lines[index] = self.lines[index][:-2].strip()
                elif self.lines[index].endswith('\\nl'):
                    self.lines[index] = self.lines[index][:-3].strip()
                self.lines[index] = self.lines[index].replace('\\ ', '& ') # Replace delimiters with ' & '

                # Add line number in second position
                first_break = self.lines[index].find('&')
                self.lines[index] = self.lines[index][:first_break + 1] + ' ({0}) &'.format(line_count) + self.lines[index][first_break + 1:]

                line_count += 1
                if self.lines[index].endswith('\\'):
                    self.lines[index] = self.lines[index][:-1] + '&'

                if self.lines[index].strip().endswith(' P'):
                    # Check if lazy and left an extra column blank because of premise
                    if self.lines[index].count('&') == expected_columns - 2:
                        self.lines[index] = self.lines[index][:self.lines[index].rindex('&') + 1] + ' &' + self.lines[index][self.lines[index].rindex('&') + 1:]
                self.lines[index] += ' \\\\' # Re-add newline characters after each line
                
                # MP -> \text{MP}, MT -> \text{MT}, etc. 
                self.lines[index] = self._apply_tfds_rules_names(self.lines[index])
                
            index += 1

        """
        ALIGNMENT
        """
        start_align = None
        index = 0
        while index < len(self.lines):
            lower_case = self.lines[index].lower()
            start_align = self._align_helper(lower_case, index, 'left', 'flushleft', start_align)
            start_align = self._align_helper(lower_case, index, 'right', 'flushright', start_align)
            start_align = self._align_helper(lower_case, index, 'center', 'center', start_align)
            if lower_case.startswith('..align justify'):
                if start_align:
                    self.lines[index] = '\\end{{{0}}}'.format(start_align)
                else:
                    self.lines.pop(index)
                start_align = None
            index += 1

        self.start_align = start_align

    # Current rules: ['MP', 'MT', 'DN', 'MCND', 'CNJ', 'CA', 'RAA', 'BIC', 'DIL', 'DM', 'D', 'P', 'W']
    def _apply_tfds_rules_names(self, line):
        for name in self.tfds_rules:
            line = line.replace(name, '\\text{' + name + '}')
        return line

    def _align_helper(self, lower_case, i, word, second_word, start_align):
        if lower_case.startswith('..align ' + word):
            if start_align:
                self.lines[i] = '\\end{{{0}}}'.format(start_align)
            self.lines.insert(i+1, '')
            self.lines.insert(i+2, '\\begin{' + second_word + '}')
            if not start_align:
                self.lines.pop(i)
            start_align = second_word
        return start_align

    def check_for_full_pream(self, _not_self_lines=''):
        if '\n..begin full preamble' in _not_self_lines and '\n..end full preamble' in _not_self_lines:
            start = _not_self_lines.index('..begin full preamble') + len('..begin full preamble')
            end = _not_self_lines.index('..end full preamble')
            self._full_preamble = '% Here is your full preamble, unmodified in any way\n\n' + _not_self_lines[start:end].strip() + '\n\n% End of full preamble\n'
            return True

    def set_aside_preamble(self, _not_self_lines=''):
        not_self_lines = _not_self_lines.split('\n')
        self._preamble = ''
        index = 0
        set_aside = False
        while index < len(not_self_lines):
            if not_self_lines[index].startswith('..begin preamble'):
                set_aside = True
                not_self_lines.pop(index)
                continue
            elif not_self_lines[index].startswith('..end preamble'):
                set_aside = False
                not_self_lines.pop(index)
                continue
            elif set_aside:
                self._preamble += not_self_lines[index] + '\n'
                not_self_lines.pop(index)
                continue
            index += 1
        return '\n'.join(not_self_lines)

    def set_aside_ignore_markers(self, _not_self_lines=''):
        not_self_lines = _not_self_lines.split('\n')
        self._ignored_contents = []
        marker_index = 0
        index = 0
        set_aside = False
        while index < len(not_self_lines):
            if not_self_lines[index].startswith('..begin ignore'):
                set_aside = True
                self.ignored_contents.append('')
                not_self_lines[index] = '\\\\marker{0}//'.format(marker_index)
            elif not_self_lines[index].startswith('..end ignore'):
                set_aside = False
                marker_index += 1
                not_self_lines.pop(index)
                continue
            elif set_aside:
                self._ignored_contents[marker_index] += not_self_lines[index] + '\n'
                not_self_lines.pop(index)
                continue
            index += 1
        return '\n'.join(not_self_lines)

    @property
    def copied_text(self):
        return self.copy_dict

    @property
    def full_preamble(self):
        return self._full_preamble

    @property
    def ignored_contents(self):
        return self._ignored_contents
    
    @property
    def preamble(self):
        return self._preamble

    @property
    def end_align(self):
        return self.start_align

    @property
    def theorem_def(self):
        output = ''

        if 'Theorem' not in self.all_theorem_names and 'theorem' not in self.all_theorem_names:
            output += '\\newtheorem{Theorem}{Theorem}\n'
        if 'Corollary' not in self.all_theorem_names and 'corollary' not in self.all_theorem_names:
            output += '\\newtheorem{Corollary}{Corollary}[Theorem]\n'
        if 'Lemma' not in self.all_theorem_names and 'lemma' not in self.all_theorem_names:
            output += '\\newtheorem{Lemma}[equation]{Lemma}\n'

        if not self.equation_numbering:
            output += '\\numberwithin{equation}{section}\n'
        else:
            output += '\\numberwithin{equation}{' + self.equation_numbering.strip() + '}\n'

        for theorem in self.unnumbered_theorems:
            output += '\\newtheorem*{{{0}}}{{{0}}}\n'.format(theorem[0].upper() + theorem[1:])
        for theorem in self.numbered_theorems:
            if len(theorem) == 1:
                output += '\\newtheorem{{{0}}}{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:])
            elif 'sub' in theorem[2].lower():
                if theorem[1].lower() == 'section':
                    output += '\\newtheorem{{{0}}}{{{0}}}[{1}]\n'.format(theorem[0][0].upper() + theorem[0][1:], 'section')
                else:
                    output += '\\newtheorem{{{0}}}{{{0}}}[{1}]\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
            else:
                if theorem[1].lower() == 'section':
                    output += '\\newtheorem{{{0}}}{{{0}}}[{1}]\n'.format(theorem[0][0].upper() + theorem[0][1:], 'section')
                else:
                    output += '\\newtheorem{{{0}}}[{1}]{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
        return output