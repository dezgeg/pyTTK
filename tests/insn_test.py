import unittest
from nose.tools import eq_, ok_

from pyttk.cpu.insn import *

def test_Opcodes():
	eq_(Opcodes.SVC, 112)
	eq_(Opcodes.COMP, 31)

	eq_(Opcodes.opcode_table[112], (OpcodeClass.SIMULATOR, 'SVC'))
	eq_(Opcodes.opcode_table[19], (OpcodeClass.ALU_CHECK_OVERFLOW, 'MUL'))

def test_Insn():
	insn = Insn(1891631115) # svc sp, =halt

	eq_(insn.opcode, Opcodes.SVC)
	eq_(insn.rj, Registers.SP)
	eq_(insn.address_mode, AddressModes.IMMEDIATE)
	eq_(insn.ri, Registers.R0)
	eq_(insn.imm_value, Svcs.HALT)

