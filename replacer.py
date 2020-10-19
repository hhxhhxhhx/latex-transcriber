
from replacers import *

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
        self.lines = sections.replace(self.lines, find_index)

        """
        COPY
        """
        self.lines, self.copy_dict = copy_paste.replace(self.lines)
        
        """
        BEGIN AND END THEOREMS
        """
        self.lines = bgn_end_thm.replace(self.lines, find_index)

        """
        PROOFS
        """
        self.lines = proofs.replace(self.lines, find_index)

        """
        LISTS
        """
        self.lines = lists.replace(self.lines)

        """
        PARTS (With inspiration from CS 70's header.sty)
        """
        self.lines = parts.replace(self.lines)

        """
        EQUATIONS
        """
        self.lines = equations.replace(self.lines)

        """
        MATRICES
        """
        self.lines = matrices.replace(self.lines)

        """
        TABLES / ARRAYS
        """
        self.lines = tables.replace(self.lines)


        """
        TFDS
        """
        self.lines = tfds.replace(self.lines)

        """
        ALIGNMENT
        """
        self.lines, self.start_align = alignment.replace(self.lines)

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
