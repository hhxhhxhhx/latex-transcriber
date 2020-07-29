
import sys

if len(sys.argv) == 1:
	sys.exit(0)

def load_pairs(fil: str = 'pairs.txt'):
    with open(fil, 'r') as f:
        contents = f.read().split('\n')
        contents = [x for x in contents if x]
        #print(contents)

        pairs = [x.split(' -> ') for x in contents]
        for pair in pairs:
	        if ' %' in pair[1]:
	            pair[1] = pair[1][:pair[1].index(' %')]
        return pairs

def find_index(lst, strr):
	for i in range(len(lst)):
		if strr in lst[i]:
			return i
	return -1

def find_content(lst, strr, deff=None):
    for item in lst:
        if strr in item:
            ret = item[item.index(strr) + len(strr):]
            while len(ret) > 0 and ret[-1] == ' ':
                ret = ret[:-1]
            return ret
    return deff

pytex = sys.argv[1]
print("File to transcribe from:", pytex)

pairs = load_pairs()
#print(pairs)

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
	elif len(lines[i]) > 1 and '%' == lines[i][0]:
		lines[i] = ''

lines = [x for x in lines if x]

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

_start = find_index(lines, '..begin')
_end = find_index(lines, '..end')
if _end < _start:
	sys.exit(1)

_content = "\n".join(lines[_start + 1: _end])

for pair in pairs:
	_content = _content.replace(pair[0], pair[1])

output = '\n\\documentclass[{0}pt]{{article}}\n'.format(font)
output += '\\usepackage{'
for package in packages[:-1]:
	output += package + ', '
output += packages[-1] + '}\n'

output += '\\geometry{{{0}paper, {1}, margin={2}in}}\n'.format(paper, orientation, margin)

output += '\\setlength{{\\parindent}}{{{0}em}}\n'.format(indent)

output += '\\setlength{{\\linespread}}{{{0}}}\n'.format(line_spread)

# Add the stuff regarding creating new commands

output += '\n'

output += "\\begin{document}\n\n"

output += _content

output += "\n\n\\end{document}\n"

output += "\n% Created by python -> latex autotranscriber\n"
print(output)

with open('output.tex', 'w') as f:
	f.write(output)
