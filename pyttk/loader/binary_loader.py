import re

import pyttk
from pyttk.loader.program import Program, Segment

symtab_line = re.compile(r'([a-zA-Z_][_a-zA-Z0-9]*)\s+(\d+)')

def load_binary_file(filename, stream=None):
	if not stream:
		stream = open(filename)
	return BinaryLoader(filename, stream).load()

class LoadError(Exception):
	"""An exception class for the binary loader. """

class BinaryLoader:
	def __init__(self, filename, stream):
		self.filename = filename
		self.stream = stream
		self.line_number = 0

	def raise_error(self, msg):
		full_msg = "%s at '%s' line %d" % (msg, self.filename, self.line_number)
		raise LoadError(full_msg)
	
	def get_line(self):
		line = self.stream.readline()
		if line == '':
			self.raise_error('Unexpected end of file')
		self.line_number += 1
		return line.strip()

	def load(self):
		self.program = Program()

		if self.get_line() != '___b91___':
			self.raise_error('B91 file magic not found')

		got_end = False
		while not got_end:
			line = self.get_line()
			if line == '___code___':
				if self.program.code_seg:
					self.raise_error('duplicate code segment entry')
				self.program.code_seg = self.parse_segment()
			elif line == '___data___':
				if self.program.data_seg:
					self.raise_error('duplicate data segment entry')
				self.program.data_seg = self.parse_segment()
			elif line == '___symboltable___':
				while True:
					entry = self.get_line()
					if entry == '___end___':
						got_end = True
						break
					match = symtab_line.match(entry)
					if not match:
						self.raise_error('bad symbol table entry')
					value = int(match.group(2))
					if not (pyttk.TTK_INT_MIN <= value <= pyttk.TTK_INT_MAX):
						self.raise_error('symbol table value out of range')
					self.program.symbol_table[match.group(1)] = value
		if self.program.code_seg is None:
			self.raise_error('file did not contain code segment')
		if self.program.data_seg is None:
			self.raise_error('file did not contain data segment')
		if self.program.data_seg.start < self.program.code_seg.end:
			self.raise_error('data segment must be located after code segment')
		# TODO: check for overlapping code & data segments
		return self.program

	def parse_segment(self):
		line = self.get_line()
		try:
			(start, end) = map(int, line.split(None, 1))
		except Exception:
			self.raise_error('malformed segment location specification')
		segment = Segment(start, end)
		for i in range(end - start + 1):
			value = int(self.get_line())
			if not pyttk.TTK_INT_MIN <= value <= pyttk.TTK_INT_MAX:
				self.raise_error('segment data value out of range')
			segment.data[i] = value
		return segment	
