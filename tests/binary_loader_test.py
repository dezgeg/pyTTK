import unittest
from nose.tools import eq_, ok_

from StringIO import StringIO

from pyttk.loader.binary_loader import load_binary_file

class BinaryLoaderSuccesfulLoadTests(unittest.TestCase):
	def setUp(self):
		self.program = load_binary_file('test file', StringIO("""___b91___
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
___end___
"""))

	def test_code_seg_correct(self):
		cseg = self.program.code_seg
		eq_(cseg.start, 0)
		eq_(cseg.end, 1)

		eq_(cseg.data[0], 35651626)
		eq_(cseg.data[1], 1891631115)

	def test_data_seg_correct(self):
		dseg = self.program.data_seg
		eq_(dseg.start, 2)
		eq_(dseg.end, 3)

		eq_(dseg.data[0], 42)
		eq_(dseg.data[1], -1337)
	
	def test_symbol_table_correct(self):
		symtab = self.program.symbol_table

		eq_(len(symtab), 2)
		eq_(symtab['test'], 2)
		eq_(symtab['halt'], 11)
