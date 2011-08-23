import array
class Segment:
	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.data = array.array('l',
			(0 for _ in xrange(start, end + 1)))

class Program:
	def __init__(self):
		self.code_seg = self.data_seg = None
		self.symbol_table = {}
