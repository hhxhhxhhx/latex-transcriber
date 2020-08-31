
import os
import sys
import subprocess
from datetime import datetime
import time
import pytz

def _print(*args):
    for item in args:
        sys.stdout.write(item + ' ')
    sys.stdout.write('\n')
    sys.stdout.flush()

if len(sys.argv) == 1:
    sys.exit(0)

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
    pytex = sys.argv[1]
    pairs = load_pairs()

    with open(pytex, 'r') as f:
        content = f.read()

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
    packages = ['amsmath', 'amssymb', 'amsthm', 'geometry']
    packages.extend(find_content(lines, '..usepackage', '').split())

    # Set page size
    paper = find_content(lines, '..paper', 'letter')

    # Set page orientation
    orientation = find_content(lines, '..orient', 'portrait')

    # Set margin
    margin = find_content(lines, '..margin', '1')

    # Set indent
    indent = find_content(lines, '..indent', '4')

    # Set spacing
    spacing = find_content(lines, '..spacing', '1.5')
    line_spread = 1.3
    if spacing == '1':
        line_spread = 1.0
    elif spacing == '2':
        line_spread = 1.6

    pagenumbering = find_content(lines, '..pagenumber', 'bottom')
    if pagenumbering.lower() == 'bottom':
        pagenumbering = 'plain'
    elif pagenumbering.lower() == 'none':
        pagenumbering = 'empty'

    qed_symbol = find_content(lines, '..qed', '$\\blacksquare$')

    replacer = Replacer(lines)

    replacer.replace()

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

    output += '\\pagestyle{{{0}}}\n'.format(pagenumbering)

    output += '\n'

    if '\\norm' in _content:
        output += '\\newcommand{\\norm}[1]{\\|#1\\|}\n'
    if '\\pytexdef' in _content:
        output += '\\newcommand{\\pytexdef}{\\mathrel{\\stackrel{\\makebox[0pt]{\\mbox{\\normalfont\\tiny def}}}{=}}}\n'
    if '\\pytexset' in _content:
        output += '\\newcommand{\\pytexset}{\\mathrel{\\stackrel{\\makebox[0pt]{\\mbox{\\normalfont\\tiny set}}}{=}}}\n'

    output += '\\renewcommand\\qedsymbol{{{0}}}\n'.format(qed_symbol)

    output += '\n'

    output += replacer.theorem_def

    output += '\n'

    output += "\\begin{document}\n"

    output += "\n\\begin{flushleft}\n"

    output += _content

    end_align = replacer.end_align
    if end_align:
        output += '\n\\end{{{0}}}\n'.format(end_align)

    output += "\n\\end{document}\n"

    tex_file_name = sys.argv[1][:sys.argv[1].index('.')] + '.tex'

    with open(tex_file_name, 'w') as f:
        f.write(output)

    _print("Successfully transcribed to {0}!".format(tex_file_name))

    try:
        exe = subprocess.run(['pdflatex', tex_file_name], timeout=2, capture_output=True)
        _print("Successfully compiled to {0}.pdf!".format(tex_file_name[:-4]))
    except Exception:
        _print("An error has occured. Please manually compile the file.")
    
    return tex_file_name[:-4]



# Replacer class

class Replacer():

    # Set up \newtheorem and \newtheorem* commands
    def __init__(self, lines):
        self.lines = lines

    def replace(self):

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
                self.lines[_beginsection] = '\\{0}section{{{1}}}'.format('sub' * i, text)
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
                    self.lines[i] = '    '*nested_list_total + '\\begin{itemize}'
                    nested_list_names.append('itemize')
                else: # Other lists do have numbering
                    self.lines[i] = '    '*nested_list_total + '\\begin{enumerate}'
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
    contents = ['..union -> \\cup', 
                '..itsc -> \\cap', 
                '..<< -> \\ll', 
                '..>> -> \\gg', 
                '..~= -> \\approx', 
                '..setdiff -> \\setminus', 
                '..del -> \\nabla', 
                '..<( -> \\langle', 
                '..>) -> \\rangle', 
                '..norm -> \\norm', 
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
                '..set= -> \\pytexset', 
                '..set -> \\mathbb',
                '..nin -> \\notin', 
                '..it -> \\emph', 
                '..bd -> \\textbf', 
                '..n -> \\\\', 
                '..t -> \\quad']
    pairs = [x.split(' -> ') for x in contents]
    for pair in pairs:
        if ' %' in pair[1]:
            pair[1] = pair[1][:pair[1].index(' %')]
    return pairs

if __name__ == "__main__":
    file_name = main()
    if os.path.exists(file_name + '.aux'):
        os.remove(file_name + '.aux')
    if os.path.exists(file_name + '.log'):
        os.remove(file_name + '.log')
