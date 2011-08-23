import unittest
from nose.tools import eq_, ok_

from StringIO import StringIO

from pyttk.loader.binary_loader import load_binary_file

class BinaryLoaderSuccesfulLoadTests(unittest.TestCase):
	def setUp(self):
		self.program = load_binary_file('test file', StringIO(
"""___b91___
___code___
0 1
35651626
1891631115
___data___
2 3
42
-1337
___symboltable___
test 2
halt 11
___end___"""))

	def test_code_seg_correct(self):
		cseg = self.program.code_seg

		eq_(len(cseg), 2)
		eq_(cseg.start, 0)
		eq_(cseg.end, 1)

		eq_(cseg.data[0], 35651626)
		eq_(cseg.data[1], 1891631115)

	def test_data_seg_correct(self):
		dseg = self.program.data_seg

		eq_(len(dseg), 2)
		eq_(dseg.start, 2)
		eq_(dseg.end, 3)

		eq_(dseg.data[0], 42)
		eq_(dseg.data[1], -1337)
	
	def test_symbol_table_correct(self):
		symtab = self.program.symbol_table

		eq_(len(symtab), 2)
		eq_(symtab['test'], 2)
		eq_(symtab['halt'], 11)

	def test_init_sp_fp_correct(self):
		eq_(self.program.get_init_sp(), 3)
		eq_(self.program.get_init_fp(), 1)

class BinaryLoaderEmptyDataSegmentTests(unittest.TestCase):
	def setUp(self):
		self.program = load_binary_file('test file with no data segment',
				StringIO(
"""___b91___
___code___
0 1
35651626
1891631115
___data___
2 1
___symboltable___
halt 11
___end___"""))

	def test_data_seg_correct(self):
		eq_(len(self.program.data_seg), 0)

	def test_init_sp_fp_correct(self):
		eq_(self.program.get_init_fp(), 1)
		eq_(self.program.get_init_sp(), 1)
