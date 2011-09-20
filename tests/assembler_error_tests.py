from nose.tools import(eq_, ok_)
import unittest

from pyttk.cpu.insn import *
from pyttk.assembler import Assembler

def asm(content):
	return Assembler('testfile.k91', content).build_binary()

class AssemblerErrorTests(unittest.TestCase):
	def assertIn(self, needle, haystack):
		self.assertTrue(needle in haystack, '%r in %r' % (needle, haystack))
	def test_equ_without_label(self):
		res = asm('equ 42')
		self.assertIn('testfile.k91:1 equ without a label', res[0])

	def test_ds_negative_arg(self):
		res = asm('foo ds -2')
		self.assertIn("testfile.k91:1 operand to 'ds' must be positive", res[0])

	def test_missing_operands(self):
		res = asm("load")
		self.assertIn('testfile.k91:1 instruction requires a first operand', res[0])

	def test_missing_second_operand(self):
		res = asm('add r1')
		self.assertIn('testfile.k91:1 instruction requires a second operand', res[0])

	def test_immediate_to_memory_insn(self):
		res = asm('store r1, r4')
		self.assertIn('testfile.k91:1 instruction requires a memory operand', res[0])

class AssemblerMessageTests(unittest.TestCase):
	def test_error_line_numbers(self):
		res = asm("""	;this line is empty
		add r1, r2 ; this line has no errors

		pop r1, 42 ; error!""")
		self.assertTrue('testfile.k91:4 second operand to POP must be a register' in res[0])

	def test_multiple_errors(self):
		result = asm("""add r1, =r1
		; empty line
		store r1, r1
		""")
		ok_(result[0].startswith('testfile.k91:1 '))
		ok_(result[1].startswith('testfile.k91:3 '))
