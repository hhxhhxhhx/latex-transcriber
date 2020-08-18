
import sys
import subprocess
from datetime import datetime
import time
import pytz
from command_replacer import Replacer

def _print(*args):
    for item in args:
        sys.stdout.write(item + ' ')
    sys.stdout.write('\n')
    sys.stdout.flush()

if len(sys.argv) == 1:
	sys.exit(0)

def load_pairs(fil: str = 'pairs.txt'):
    with open(fil, 'r') as f:
        contents = f.read().split('\n')
        contents = [x for x in contents if x]

        pairs = [x.split(' -> ') for x in contents]
        for pair in pairs:
	        if ' %' in pair[1]:
	            pair[1] = pair[1][:pair[1].index(' %')]
        return pairs

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
packages.extend(find_content(lines, '..package', '').split())

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
if spacing.lower() == 'single' or spacing.lower() == '1':
    line_spread = 1.0
elif spacing.lower() == 'double' or spacing.lower() == '2':
    line_spread = 1.6

pagenumbering = find_content(lines, '..pagenumber', 'bottom')
if pagenumbering.lower() == 'bottom':
    pagenumbering = 'plain'
elif pagenumbering.lower() == 'none':
    pagenumbering = 'empty'

qed_symbol = find_content(lines, '..qed', '$\\blacksquare$')

replacer = Replacer(lines, find_content, find_index)

replacer.replace()

_start = find_index(lines, '..begin main')
_end = find_index(lines, '..end main')

main_content = lines[_start + 1: _end]

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
output += "% Compiled on {0}-{1}-{2} {3}:{4}:{5} PDT\n\n".format(time_rn.year , time_rn.month, time_rn.day, time_rn.hour, time_rn.minute, time_rn.second)

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

_print()
_print("Successfully transcribed to {0}!".format(tex_file_name))

try:
    exe = subprocess.run(['pdflatex', tex_file_name], timeout=3, capture_output=True)
    _print()
    _print("Successfully compiled to {0}.pdf!".format(tex_file_name[:-4]))
except Exception:
    _print("An error has occured. Please manually compile the file.")
