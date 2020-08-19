
class Replacer():

	# Set up \newtheorem and \newtheorem* commands
	def __init__(self, lines, find_content, find_index):
		self.lines = lines
		self.find_content = find_content
		self.find_index = find_index

	def replace(self):

		"""
		INITIALIZING THEOREMS
		"""
		self.all_theorem_names = []
		_initunnumberedtheorem = self.find_content(self.lines, '..initheorem*', None) # Unnumbered theorems to be defined using ..initheorem*
		self.unnumbered_theorems = []
		while _initunnumberedtheorem:
			lst = _initunnumberedtheorem.split()
			# These theorems must have 1 argument: the name of the type of theorem
			if len(lst) != 1:
				print("Error with ..initheorem* {0} command!".format(_initunnumberedtheorem))
			else:
				self.unnumbered_theorems.append(lst[0])
				self.all_theorem_names.append(lst[0])
				line_to_remove = self.find_index(self.lines, '..initheorem*')
				self.lines.pop(line_to_remove)
				_initunnumberedtheorem = self.find_content(self.lines, '..initheorem*', None)

		_initnumberedtheorem = self.find_content(self.lines, '..initheorem', None) # Numbered theorems to be defined using ..initheorem
		self.numbered_theorems = []
		while _initnumberedtheorem:
			lst = _initnumberedtheorem.split()
			# Must have 1 or 3 arguments: 1 if the counter is by itself
			#							  3 if the counter is subordinate or shared with something else
			if len(lst) != 1 and len(lst) != 3:
				print("Error with ..initheorem {0} command!".format(_initnumberedtheorem))
			else:
				self.numbered_theorems.append(lst)
				self.all_theorem_names.append(lst[0])
				line_to_remove = self.find_index(self.lines, '..initheorem')
				self.lines.pop(line_to_remove)
				_initnumberedtheorem = self.find_content(self.lines, '..initheorem', None)

		# Check for ..begin section or ..begin subsection or ..begin subsubsection, etc. 
		for i in range(5):
			_beginsection = self.find_index(self.lines, '..begin {0}section'.format('sub' * i))
			while _beginsection != -1:
				text = self.lines[_beginsection][len('..begin {0}section'.format('sub' * i)) + 1:].strip()
				self.lines[_beginsection] = '\\{0}section{{{1}}}'.format('sub' * i, text)
				_beginsection = self.find_index(self.lines, '..begin {0}section'.format('sub' * i))

		"""
		BEGIN AND END THEOREMS
		"""
		_begintheorem = self.find_index(self.lines, '..begin thm')
		while _begintheorem != -1:
			text = self.lines[_begintheorem][12:].split()
			if len(text) == 1:
				self.lines[_begintheorem] = '\\begin{{{0}}}'.format(text[0][0].upper() + text[0][1:])
			else:
				self.lines[_begintheorem] = '\\begin{{{0}}}[{1}]'.format(text[0][0].upper() + text[0][1:], " ".join(text[1:]))
			_begintheorem = self.find_index(self.lines, '..begin thm')

		_endtheorem = self.find_index(self.lines, '..end thm')
		while _endtheorem != -1:
			text = self.lines[_endtheorem][10:].split()
			self.lines[_endtheorem] = '\\end{{{0}}}'.format(text[0][0].upper() + text[0][1:])
			_endtheorem = self.find_index(self.lines, '..end thm')


		"""
		SAME THING BUT PROOFS
		"""
		_beginproof = self.find_index(self.lines, '..begin proof')
		while _beginproof != -1:
			self.lines[_beginproof] = '\\begin{proof}'
			_beginproof = self.find_index(self.lines, '..begin proof')

		_endproof = self.find_index(self.lines, '..end proof')
		while _endproof != -1:
			self.lines[_endproof] = '\\end{proof}'
			_endproof = self.find_index(self.lines, '..end proof')


		"""
		LISTS
		"""
		nested_list_total = 0 # Used to indent
		nested_list_names = []
		for	i in range(len(self.lines)):
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
