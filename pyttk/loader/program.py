import array
class Segment:
	def __init__(self, start, end, contents=None):
		self.start = start
		self.end = end
		self.data = array.array('l',
			contents if contents else (0 for _ in xrange(start, end + 1)))

	def __len__(self):
		return self.end - self.start + 1

	def __getitem__(self, i):
		return self.data[i - self.start]

class Program:
	def __init__(self):
		self.code_seg = self.data_seg = None
		self.symbol_table = {}

	def get_init_sp(self):
		return self.data_seg.end

	def get_init_fp(self):
		return self.code_seg.end

	def get_init_pc(self):
		return self.code_seg.start
