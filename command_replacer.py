
class Replacer():

	# Set up \newtheorem and \newtheorem* commands
	def __init__(self, lines, find_content, find_index):
		self.lines = lines
		self.find_content = find_content
		self.find_index = find_index

	def replace(self):

		self.all_theorem_names = []
		_initunnamedtheorem = self.find_content(self.lines, '..initheorem*', None)
		self.unnamed_theorems = []
		while _initunnamedtheorem:
			lst = _initunnamedtheorem.split()
			if len(lst) != 1:
				print("Error with ..initheorem* {0} command!".format(_initunnamedtheorem))
			else:
				self.unnamed_theorems.append(lst[0])
				self.all_theorem_names.append(lst[0])
				line_to_remove = self.find_index(self.lines, '..initheorem*')
				self.lines.pop(line_to_remove)
				_initunnamedtheorem = self.find_content(self.lines, '..initheorem*', None)

		_initnamedtheorem = self.find_content(self.lines, '..initheorem', None)
		self.named_theorems = []
		while _initnamedtheorem:
			lst = _initnamedtheorem.split()
			if len(lst) != 1 and len(lst) != 3:
				print("Error with ..initheorem {0} command!".format(_initnamedtheorem))
			else:
				self.named_theorems.append(lst)
				self.all_theorem_names.append(lst[0])
				line_to_remove = self.find_index(self.lines, '..initheorem')
				self.lines.pop(line_to_remove)
				_initnamedtheorem = self.find_content(self.lines, '..initheorem', None)

		# Replace all '..beginthm' with \begin{theorem}
		_begintheorem = self.find_index(self.lines, '..beginthm')
		while _begintheorem != -1:
			text = self.lines[_begintheorem][11:].split()
			if len(text) == 1:
				self.lines[_begintheorem] = '\\begin{{{0}}}'.format(text[0][0].upper() + text[0][1:])
			else:
				self.lines[_begintheorem] = '\\begin{{{0}}}[{1}]'.format(text[0][0].upper() + text[0][1:], " ".join(text[1:]))
			_begintheorem = self.find_index(self.lines, '..beginthm')

		# Replace all '..endthm' with \end{theorem}
		_endtheorem = self.find_index(self.lines, '..endthm')
		while _endtheorem != -1:
			text = self.lines[_endtheorem][9:].split()
			self.lines[_endtheorem] = '\\end{{{0}}}'.format(text[0][0].upper() + text[0][1:])
			_endtheorem = self.find_index(self.lines, '..endthm')

		_beginproof = self.find_index(self.lines, '..beginproof')
		while _beginproof != -1:
			self.lines[_beginproof] = '\\begin{proof}'
			_beginproof = self.find_index(self.lines, '..beginproof')

		_endproof = self.find_index(self.lines, '..endproof')
		while _endproof != -1:
			self.lines[_endproof] = '\\end{proof}'
			_endproof = self.find_index(self.lines, '..endproof')

		nested_list_total = 0
		nested_list_names = []
		for	i in range(len(self.lines)):
			if nested_list_total and self.lines[i].strip().startswith('.. '):
				self.lines[i] = '    '*nested_list_total + '\\item ' + self.lines[i].strip()[3:]
			elif self.lines[i].strip().startswith('..beginlist'):
				if len(self.lines[i].strip()) > 11 and self.lines[i].strip()[12:].strip() == 'bullet':
					self.lines[i] = '    '*nested_list_total + '\\begin{itemize}'
					nested_list_names.append('itemize')
				else:
					self.lines[i] = '    '*nested_list_total + '\\begin{enumerate}'
					nested_list_names.append('enumerate')
				nested_list_total += 1
			elif self.lines[i].strip().startswith('..endlist'):
				nested_list_total -= 1
				self.lines[i] = '    '*nested_list_total + '\\end{{{0}}}'.format(nested_list_names.pop())
			elif nested_list_total and not self.lines[i].strip().startswith('.. '):
				self.lines[i] = '    '*nested_list_total + self.lines[i].strip()

	def get_output(self):
		output = ''
		if 'Theorem' not in self.all_theorem_names and 'theorem' not in self.all_theorem_names:
			output += '\\newtheorem{Theorem}{Theorem}\n'
		if 'Corollary' not in self.all_theorem_names and 'corollary' not in self.all_theorem_names:
			output += '\\newtheorem{Corollary}{Corollary}[Theorem]\n'
		if 'Lemma' not in self.all_theorem_names and 'lemma' not in self.all_theorem_names:
			output += '\\newtheorem{Lemma}[Theorem]{Lemma}\n'

		for theorem in self.unnamed_theorems:
			output += '\\newtheorem*{{{0}}}{{{0}}}\n'.format(theorem[0].upper() + theorem[1:])
		for theorem in self.named_theorems:
			if len(theorem) == 1:
				output += '\\newtheorem{{{0}}}{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:])
			elif 'sub' in theorem[2].lower():
				output += '\\newtheorem{{{0}}}{{{0}}}[{1}]\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
			else:
				output += '\\newtheorem{{{0}}}[{1}]{{{0}}}\n'.format(theorem[0][0].upper() + theorem[0][1:], theorem[1][0].upper() + theorem[1][1:])
		return output