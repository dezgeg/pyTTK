from nose.tools import(eq_, ok_)
import unittest

from pyttk.cpu.insn import *
from pyttk.assembler import Assembler

def asm(content):
	return Assembler('testfile.k91', content).build_binary()

class AssemblerErrorTests(unittest.TestCase):
	def test_equ_without_label(self):
		res = asm('equ 42')
		eq_(res, ['testfile.k91:1 equ without a label'])

	def test_ds_negative_arg(self):	
		res = asm('foo ds -2')
		eq_(res, ["testfile.k91:1 operand to 'ds' must be positive"])

	def test_missing_operands(self):
		res = asm("load")
		eq_(res, ['testfile.k91:1 instruction requires a first operand'])

	def test_missing_second_operand(self):
		res = asm('add r1')
		eq_(res, ['testfile.k91:1 instruction requires a second operand'])

	def test_immediate_to_memory_insn(self):
		res = asm('store r1, r4')
		eq_(res, ['testfile.k91:1 instruction requires a memory operand'])

class AssemblerMessageTests(unittest.TestCase):
	def test_error_line_numbers(self):
		res = asm("""   ;this line is empty
		add r1, r2 ; this line has no errors

		pop r1, 42 ; error!""")
		eq_(res, ['testfile.k91:4 second operand to POP must be a register'])

	def test_multiple_errors(self):
		res = asm("""add r1, =r1
		; empty line
		store r1, r1
		""")
		eq_(res, ['testfile.k91:1 OPER Rj, =Ri form not allowed',
			'testfile.k91:3 instruction requires a memory operand'])
