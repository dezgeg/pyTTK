import unittest
from nose.tools import eq_, ok_

from pyttk.cpu.insn import *

def test_Opcodes():
	eq_(Opcodes.SVC, 112)
	eq_(Opcodes.COMP, 31)

	svc = Opcodes.opcode_table[112]
	mul = Opcodes.opcode_table[19]

	eq_(svc.op_class, OpcodeClass.SIMULATOR)
	eq_(svc.mnemoic, 'SVC')
	eq_(svc.flags, 0)

	eq_(mul.op_class, OpcodeClass.ALU_CHECK_OVERFLOW)
	eq_(mul.mnemoic, 'MUL')
	eq_(mul.flags, 0)

def test_Insn_word_ctor():
	insn = Insn(1891631115) # svc sp, =halt

	eq_(insn.opcode, Opcodes.SVC)
	eq_(insn.rj, Registers.SP)
	eq_(insn.address_mode, AddressModes.IMMEDIATE)
	eq_(insn.ri, Registers.R0)
	eq_(insn.imm_value, Svcs.HALT)

	eq_(insn.to_binary(), 1891631115)

def test_Insn_parts_ctor():
	insn = Insn(Opcodes.LOAD, 1, AddressModes.IMMEDIATE, 2, 42)

	eq_(insn.opcode, Opcodes.LOAD)
	eq_(insn.rj, Registers.R1)
	eq_(insn.address_mode, AddressModes.IMMEDIATE)
	eq_(insn.ri, Registers.R2)
	eq_(insn.imm_value, 42)

	eq_(insn.to_binary(), 35782698)
