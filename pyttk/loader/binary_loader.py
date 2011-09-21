import re

import pyttk
from pyttk.loader.program import Program, Segment

symtab_line = re.compile(r'([a-zA-Z_][_a-zA-Z0-9]*)\s+(\d+)')

def load_binary_file(filename, stream=None):
	if not stream:
		stream = open(filename)
	return BinaryLoader(filename, stream).load()

class LoadError(Exception):
	"""A simple exception class for the binary loader. """

class BinaryLoader:
	"""A class that contains methods to load TTK-91 B91 binary files. """
	def __init__(self, filename, stream):
		"""function:: BinaryLoader(filename, stream)

		Creates a new TTK-91 B91 binary file loader instance for one file.
		:param filename: File name used for error messages
		:param stream: The file stream object whose contents are to be loaded.
		"""
		self.filename = filename
		self.stream = stream
		self.line_number = 0

	def raise_error(self, msg):
		"""Raise a :class:`LoadError` exception indicating that loading the binary file failed for some reason

		:param msg: An informational message that should tell the user why the loading failed
		:raises: A :class:`LoadError` instance, whose message string contains the current file, line, and the specified error message.
		"""
		full_msg = "%s at '%s' line %d" % (msg, self.filename, self.line_number)
		raise LoadError(full_msg)
	
	def get_line(self):
		"""Read a line from the input file, raising an error if end-of-file is reached.

		:rtype: string
		:returns: The next line from the input file, with the newline separator removed.
		:raises: :class:`LoadError` indicating unexpected end-of-file if end-of-file condition is reached.
		"""
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
					self.raise_error('duplicate code segment entry') # TODO: add tests for error checks
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
		"""Read a segment description from the input file.

		:returns: A new :class:`Segment` instance representing the segment read from the input file.
		:raises: A :class:`LoadError` if the input file contains invalid syntax
		"""
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
			segment[i] = value
		return segment	

	@classmethod
	def dump_binary(cls, program, stream):
		"""Dump a :class:`Program` instance to the file stream stream in the B91 binary format

		:param program: A program instance to be dumped.
		:param stream: The file stream in which the Program is to be written.
		"""
		stream.write("___b91___\n")

		cls.dump_segment(program.code_seg, '___code___', stream)
		cls.dump_segment(program.data_seg, '___data___', stream)
		cls.dump_symbol_table(program.symbol_table, stream)

		stream.write("___end___\n")

	@staticmethod
	def dump_segment(seg, headerline, stream):
		"""Dump a Segment instance with a header string `headerline` to the file stream `stream` in the format used in B91 files

		:param headerline: A header line which identifies the type of the segment, like '__code__' or '__data__'
		:param stream: The file stream in which the :class:`Segment` is to be written.
		"""
		stream.write(headerline + "\n")
		stream.write("%d %d\n" % (seg.start, seg.end))
		for val in seg:
			stream.write("%d\n" % val)

	@staticmethod
	def dump_symbol_table(symtab, stream):
		"""Dump a :class:`SymbolTable` instance to the file stream stream.

		Implementation detail: The symbol table elements are written in sorted order for convenience,
		other implementations may write them in any order. As the SymbolTable's keys are case-insensitive,
		they are converted to lowercase for compability with other implementations.

		:param symtab: A :class:`SymbolTable` instance to be dumped.
		:param stream: The file stream in which the symbol table is to be written.
		"""
		stream.write("___symboltable___\n")

		for name,val in sorted(symtab.iteritems()):
			stream.write('%s %d\n' % (name, val))

