import array
from collections import defaultdict

from pyttk.cpu.insn import Svcs, Devices
class Segment:
	def __init__(self, start, end, contents=None):
		self.start = start
		self.end = end
		self.data = array.array('l',
			contents if contents else (0 for _ in xrange(start, end + 1)))

	def to_list(self):
		return self.data.tolist()

	def __len__(self):
		return self.end - self.start + 1

	def __getitem__(self, i):
		return self.data[i - self.start]

	def __setitem__(self, i, value):
		self.data[i - self.start] = value

	def __iter__(self):
		return self.data.__iter__()

	def __eq__(self, other):
		return (self.start == other.start and
				self.end == other.end and
				self.data == other.data)

class Program:
	def __init__(self):
		self.code_seg = self.data_seg = None
		self.symbol_table = SymbolTable()

	def __eq__(self, other):
		return (self.code_seg == other.code_seg and
			self.data_seg == other.data_seg and
			self.symbol_table == other.symbol_table)

	def get_init_sp(self):
		return self.data_seg.end

	def get_init_fp(self):
		return self.code_seg.end

	def get_init_pc(self):
		return self.code_seg.start

class SymbolTable(dict):
	DEFAULT_SYMBOLS = {}
	DEFAULT_SYMBOLS.update(Svcs.SVC_NUMBERS)
	DEFAULT_SYMBOLS.update(Devices.DEVICE_NUMBERS)

	def __init__(self):
		super(SymbolTable, self).__init__()

	def __getitem__(self, key):
		key = key.lower()
		if key not in self:
			val = self.DEFAULT_SYMBOLS[key]
			self[key] = val
			return val
		return super(SymbolTable, self).__getitem__(key)

	def __setitem__(self, key, value):
		super(SymbolTable, self).__setitem__(key.lower(), value)
