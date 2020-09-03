
import os # For deleting files with -d flag
from sys import stdout # For printing out statements
import subprocess # For compiling with -c flag

from datetime import datetime
import time
import pytz

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', "--compile", action='store_true', help='attempts to use pdflatex to compile the transcribed file')
parser.add_argument('-d', "--delete", action='store_true', help='deletes the .aux and .log files generated by pdflatex')
parser.add_argument('-n', "--name", help='uses NAME to be put on the top right header. subordinate to using ..name')
parser.add_argument("-f", "--file", required=True, help='transcribes FILE')
args = parser.parse_args()

def _print(*args):
    for item in args:
        stdout.write(item + ' ')
    stdout.write('\n')
    stdout.flush()

def find_index(lst, strr):
    for i in range(len(lst)):
        if strr in lst[i] and '\\verb|' + strr not in lst[i]:
            return i
    return -1

def find_content(lst, strr, deff=None):
    for item in lst:
        if strr in item and '\\verb|' + strr not in item:
            ret = item[item.index(strr) + len(strr) + 1:]
            while len(ret) > 0 and ret[-1] == ' ':
                ret = ret[:-1]
            return ret
    return deff

def main():
    file_name = args.file

    pairs = load_pairs()

    with open(file_name, 'r') as f:
        content = f.read()

    replacer = Replacer()
    content = replacer.set_aside_preamble(content)
    content = replacer.set_aside_ignore_markers(content)

    # Remove comments
    while '%%%' in content:
        ind1 = content.index('%%%')
        ind2 = ind1 + 3 + content[ind1 + 3:].index('%%%')
        content = content[:ind1] + content[ind2 + 3:]

    lines = content.split('\n')
    for i in range(len(lines)):
        if ' %' in lines[i]:
            lines[i] = lines[i][:lines[i].index(' %')]
        elif '\t%' in lines[i]:
            lines[i] = lines[i][:lines[i].index('\t%')]
        elif len(lines[i]) > 1 and '%' == lines[i][0]:
            lines[i] = ''
        lines[i] = lines[i].strip()

    # Set font
    font = find_content(lines, '..font', '12')

    # Set packages
    packages = ['amsmath', 'amssymb', 'amsthm', 'geometry', 'enumitem', 'fancyhdr']
    packages.extend(find_content(lines, '..usepackage', '').split())

    # See if name is specified
    my_name = find_content(lines, '..name', None)

    # Set page size
    paper = find_content(lines, '..paper', 'letter')

    # Set page orientation
    orientation = find_content(lines, '..orient', 'portrait')

    # Set margin
    margin = find_content(lines, '..margin', '1')

    # Set indent
    indent = find_content(lines, '..indent', '0')

    # Set spacing
    spacing = find_content(lines, '..spacing', '1.5')
    line_spread = 1.3
    if spacing == '1':
        line_spread = 1.0
    elif spacing == '2':
        line_spread = 1.6

    qed_symbol = find_content(lines, '..qed', None)

    assignment = find_content(lines, '..assignment', None)

    replacer.replace(lines)

    _start = find_index(lines, '..begin main')
    _end = find_index(lines, '..end main')

    if _end != -1:
        main_content = lines[_start + 1: _end]
    else:
        main_content = lines[_start + 1:]

    _content = "\n".join(main_content)

    # Purposely replace ones with \verb|__pair__| with \verb|random_string + __pair__|
    for pair in pairs:
        _content = _content.replace('\\verb|{0}'.format(pair[0]), '\\verb|{0}'.format(pair[0][0] + 'afoswj' + pair[0][1:]))

    for pair in pairs:
        _content = _content.replace(pair[0], pair[1])

    for pair in pairs:
        _content = _content.replace('\\verb|{0}'.format(pair[0][0] + 'afoswj' + pair[0][1:]), '\\verb|{0}'.format(pair[0]))

    output = "\n% Created by Roger Hu's .pytex -> .tex latex transcriber\n"
    time_rn = datetime.now(pytz.timezone('America/Los_Angeles'))
    output += "% Compiled on {0} PDT\n\n".format(str(time_rn)[:-13])

    output += '\n\\documentclass[{0}pt]{{article}}\n'.format(font)
    output += '\\usepackage{'
    for package in packages[:-1]:
        output += package + ', '
    output += packages[-1] + '}\n'

    output += '\n'

    output += '\\geometry{{{0}paper, {1}, margin={2}in}}\n'.format(paper, orientation, margin)
    output += '\\setlength{{\\parindent}}{{{0}em}}\n'.format(indent)
    output += '\\linespread{{{0}}}\n'.format(line_spread)
    output += '\\pagestyle{fancy}\n'
    output += '\\fancyhf{}\n'

    if '\\norm' in _content:
        output += '\\newcommand{\\norm}[1]{\\|#1\\|}\n'
    if '\\pytexdef' in _content:
        output += '\\newcommand{\\pytexdef}{\\mathrel{\\stackrel{\\makebox[0pt]{\\mbox{\\normalfont\\tiny def}}}{=}}}\n'
    if '\\pytexset' in _content:
        output += '\\newcommand{\\pytexset}{\\mathrel{\\stackrel{\\makebox[0pt]{\\mbox{\\normalfont\\tiny set}}}{=}}}\n'
    if "\\floor" in _content:
        output += '\\newcommand{\\floor}[1]{\\left\\lfloor #1 \\right\\rfloor}\n'
    if "\\ceil" in _content:
        output += '\\newcommand{\\ceil}[1]{\\left\\lceil #1 \\right\\rceil}\n'

    if qed_symbol:
        output += '\\renewcommand\\qedsymbol{{{0}}}\n'.format(qed_symbol)

    output += '\n'
    output += '\\renewcommand{\\headrulewidth}{0pt}\n'
    output += '\\renewcommand{\\footrulewidth}{1pt}\n'
    
    if my_name:
        output += '\\rhead{{{0}}}\n'.format(my_name)
    elif args.name:
        output += '\\rhead{{{0}}}\n'.format(args.name)

    output += '\\rfoot{\\fontsize{8}{8} \\selectfont \\thepage}\n'

    if assignment:
        output += '\\lfoot{\\fontsize{8}{8} \\selectfont ' + assignment + '}\n'

    output += '\n'
    output += replacer.theorem_def
    output += '\n'

    if replacer.preamble:
        output += '% This part is unaffected by transcription\n\n'
        output += replacer.preamble
        output += '\n% End of unaffected portion\n\n'

    output += "\\begin{document}\n\n"
    output += "\\begin{flushleft}\n"

    for i in range(len(replacer.ignored_contents)):
        _content = _content.replace('\\\\marker{0}//'.format(i), '% Ignored by transcriber\n' + replacer.ignored_contents[i] + '% End ignored region')
    
    output += _content

    end_align = replacer.end_align
    if end_align:
        output += '\n\\end{{{0}}}\n'.format(end_align)

    output += "\n\\end{document}\n"

    tex_file_name = file_name[:file_name.index('.')] + '.tex'

    with open(tex_file_name, 'w') as f:
        f.write(output)

    _print("Successfully transcribed to {0}!".format(tex_file_name))

    if args.compile:
        try:
            exe = subprocess.run(['pdflatex', '{0}'.format(tex_file_name)], timeout=8, capture_output=True)
            _print("Successfully compiled to {0}.pdf!".format(tex_file_name[:-4]))
        except Exception:
            _print("An error has occured. Please manually compile the file.")
    
    return tex_file_name[:-4]


# Replacer class

class Replacer():

    # Set up \newtheorem and \newtheorem* commands

    def replace(self, lines):

        self.lines = lines

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
                print("Error with ..initheorem* {0} command!".format(_initunnumberedtheorem))
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
                print("Error with ..initheorem {0} command!".format(_initnumberedtheorem))
            else:
                self.numbered_theorems.append(lst)
                self.all_theorem_names.append(lst[0])
                line_to_remove = find_index(self.lines, '..initheorem')
                self.lines.pop(line_to_remove)
                _initnumberedtheorem = find_content(self.lines, '..initheorem', None)

        # Check for ..begin section or ..begin subsection or ..begin subsubsection, etc. 
        for i in range(5):
            _beginsection = find_index(self.lines, '..begin {0}section'.format('sub' * i))
            while _beginsection != -1:
                text = self.lines[_beginsection][len('..begin {0}section'.format('sub' * i)) + 1:].strip()
                if text.startswith('number'):
                    self.lines[_beginsection] = '\\{0}section{{{1}}}'.format('sub' * i, text[7:])
                else:
                    self.lines[_beginsection] = '\\{0}section*{{{1}}}'.format('sub' * i, text)
                _beginsection = find_index(self.lines, '..begin {0}section'.format('sub' * i))

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
        SAME THING BUT PROOFS
        """
        _beginproof = find_index(self.lines, '..begin proof')
        while _beginproof != -1:
            if self.lines[_beginproof][13:].strip():
                self.lines[_beginproof] = '\\begin{{{0}}}[Proof {1}]'.format('proof', self.lines[_beginproof][13:].strip())
            else:
                self.lines[_beginproof] = '\\begin{proof}'
            _beginproof = find_index(self.lines, '..begin proof')

        _endproof = find_index(self.lines, '..end proof')
        while _endproof != -1:
            self.lines[_endproof] = '\\end{proof}'
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
                         and not self.lines[index].strip().endswith('..n'): # Add newline character after each line break because LaTeX is dumb
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
                elif self.lines[index].endswith('..n'):
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
                elif self.lines[index].endswith('..n'):
                    self.lines[index] = self.lines[index][:-3].strip()
                self.lines[index] = self.lines[index].replace('\\ ', '& ') # Replace delimiters with ' & '
                if self.lines[index].endswith('\\'):
                    self.lines[index] = self.lines[index][:-1] + '&'
                self.lines[index] += ' \\\\' # Re-add newline characters after each line
            index += 1

        """
        ALIGNMENT
        """
        start_align = 'flushleft'
        for i in range(len(self.lines)):
            lower_case = self.lines[i].lower()
            start_align = self._align_helper(lower_case, i, 'left', 'flushleft', start_align)
            start_align = self._align_helper(lower_case, i, 'right', 'flushright', start_align)
            start_align = self._align_helper(lower_case, i, 'center', 'center', start_align)
            if lower_case.startswith('..align justify'):
                if start_align:
                    self.lines[i] = '\\end{{{0}}}'.format(start_align)
                else:
                    self.lines.pop(i)
                start_align = None

        self.start_align = start_align

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
            output += '\\newtheorem{Lemma}[Theorem]{Lemma}\n'

        for theorem in self.unnumbered_theorems:
            output += '\\newtheorem*{{{0}}}{{{0}}}\n'.format(theorem[0].upper() + theorem[1:])
        for theorem in self.numbered_theorems:
            if len(theorem) == 1:
                output += '\\newtheorem{{{0}}}{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:])
            elif 'sub' in theorem[2].lower():
                output += '\\newtheorem{{{0}}}{{{0}}}[{1}]\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
            else:
                output += '\\newtheorem{{{0}}}[{1}]{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
        return output

# End of Replacer class

def load_pairs():
    contents = ['\\union -> \\cup', 
                '\\itsc -> \\cap', 
                '\\setdiff -> \\setminus', 
                '\\del -> \\nabla', 
                '\\Q -> \\mathbb{Q}',
                '\\R -> \\mathbb{R}', 
                '\\Z -> \\mathbb{Z}', 
                '\\N -> \\mathbb{N}', 
                '\\C -> \\mathbb{C}', 
                '\\nin -> \\notin', 
                '\\ital -> \\emph', 
                '\\bold -> \\textbf', 
                '\\contradiction -> $\\Rightarrow\\Leftarrow$', 
                '..<< -> \\ll', 
                '..>> -> \\gg', 
                '..~= -> \\approx', 
                '..<( -> \\langle', 
                '..>) -> \\rangle', 
                '..dot -> \\cdot', 
                '..cross -> \\times', 
                '..<=> -> \\Leftrightarrow', 
                '..<==> -> \\iff', 
                '..!=> -> \\nRightarrow', 
                '..=> -> \\Rightarrow', 
                '..==> -> \\implies', 
                '..-> -> \\to', 
                '..--> -> \\longrightarrow', 
                '..!= -> \\neq', 
                '..<= -> \\leq', 
                '..>= -> \\geq', 
                '..and -> \\wedge', 
                '..or -> \\vee', 
                '..def -> \\pytexdef', 
                '..set -> \\pytexset', 
                '..n -> \\\\', 
                '..t -> \\quad']
    pairs = [x.split(' -> ') for x in contents]
    return pairs

if __name__ == "__main__":
    file_name = main()
    if args.delete:
        if os.path.exists(file_name + '.aux'):
            os.remove(file_name + '.aux')
        if os.path.exists(file_name + '.log'):
            os.remove(file_name + '.log')
