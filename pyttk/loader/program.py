import array
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

	def __iter__(self):
		return self.data.__iter__()

	def __eq__(self, other):
		return (self.start == other.start and
				self.end == other.end and
				self.data == other.data)

class Program:
	def __init__(self):
		self.code_seg = self.data_seg = None
		self.symbol_table = {}

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

