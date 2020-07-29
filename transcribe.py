
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

def find(lst, strr):
	for i in range(len(lst)):
		if strr in lst[i]:
			return i
	return -1

pytex = sys.argv[1]
print("File to transcribe from:", pytex)

pairs = load_pairs()
#print(pairs)

with open(pytex, 'r') as f:
	content = f.read()

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

font = '12'
packages = ['amsmath', 'amssymb', 'amsthm']

font = lines[find(lines, '..font')][7:]

packages.extend(lines[find(lines, '..packages')][11:].split())

print("font:", font)
print("packages:", packages)

_start = find(lines, '..begin')
_end = find(lines, '..end')
if _end < _start:
	sys.exit(1)

_content = "\n".join(lines[_start + 1: _end])
#print(_content)

for pair in pairs:
	_content = _content.replace(pair[0], pair[1])

#print(_content)

output = '\n\\documentclass[{0}pt]{{article}}\n'.format(font)
output += '\\usepackage{'
for package in packages[:-1]:
	output += package + ', '
output += packages[len(packages) - 1] + '}\n\n'

# Add the stuff regarding creating new commands

output += "\\begin{document}\n\n"

output += _content

output += "\n\n\\end{document}\n"

output += "\n% Created by python -> latex autotranscriber\n"
print(output)

with open('output.tex', 'w') as f:
	f.write(output)
