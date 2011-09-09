from nose.tools import(eq_, ok_)
import unittest

from pyttk.cpu.insn import *
from pyttk.assembler import Assembler

def test_Assembler_parsing():
	test_string = """
	; notice an empty line before this!
	load r1, somevar
	somearray ds 10
	pop sp, r1 ; this is a special form!

	somelabel load r1, =42
	load r2, @someptr
	load r1, @5
	someconst equ 42
	add r4, somearray(fp)
	mul fp, @someptrarray(r0)
	nop
	pushr sp"""
	asm = Assembler('test file', test_string)

	# Label Opcode Rj AddrMode ImmValue Ri
	results = [
		('', Opcodes.LOAD, 1, ' ', 'somevar', ''),
		('somearray', 'ds', '', '', 10, ''),
		('', Opcodes.POP, 6, ' ', '', 1),
		('somelabel', Opcodes.LOAD, 1, '=', 42, ''),
		('', Opcodes.LOAD, 2, '@', 'someptr', ''),
		('', Opcodes.LOAD, 1, '@', 5, ''),
		('someconst', 'equ', '', '', 42, ''),
		('', Opcodes.ADD, 4, ' ', 'somearray', 7),
		('', Opcodes.MUL, 7, '@', 'someptrarray', 0),
		('', Opcodes.NOP, '', '', '', ''),
		('', Opcodes.PUSHR, 6, '', '', '')
	]
	for i in xrange(len(asm.insns)):
		insn = asm.insns[i]
		# print (insn.label, insn.opcode, insn.rj, insn.address_mode, insn.imm_value, insn.ri)
		eq_((insn.label, insn.opcode, insn.rj, insn.address_mode, insn.imm_value, insn.ri),
				results[i])

def test_Assembler_basic_instructions():
	test_string = """
		add r1, 1(r2) ; a basic instruction
		nop ; instruction with no operands
		popr sp ; instruction with only one operand
	"""
	asm = Assembler('test file', test_string)
	binary = asm.build_binary()
	eq_(len(asm.code_seg), 3)

	eq_(asm.code_seg[0], Insn(Opcodes.ADD, 1, AddressModes.DIRECT, 2, 1))
	eq_(asm.code_seg[1].opcode, Opcodes.NOP)

	eq_(asm.code_seg[2].opcode, Opcodes.POPR)
	eq_(asm.code_seg[2].rj, Registers.SP)

	eq_(len(binary.code_seg), 3)

	eq_(binary.code_seg[0], 287965185)
	eq_(binary.code_seg[1], 524288)
	eq_(binary.code_seg[2], 919076864)


def test_Assembler_exceptional_address_modes():
	test_string = """
		; check that address mode is correct for these two
		pop sp, r0
		mul r1, @r2
		store r2, 42
		jump r5, @r4
	"""
	asm = Assembler('addr mode test file', test_string)
	binary = asm.build_binary()
	eq_(len(asm.code_seg), 4)

	eq_(asm.code_seg[0], Insn(Opcodes.POP, Registers.SP,
		AddressModes.IMMEDIATE, Registers.R0, 0))
	eq_(asm.code_seg[1], Insn(Opcodes.MUL, 1,
		AddressModes.DIRECT, Registers.R2, 0))
	eq_(asm.code_seg[2], Insn(Opcodes.STORE, 2,
		0, 0, 42))
	eq_(asm.code_seg[3], Insn(Opcodes.JUMP, 5,
		0, 4, 0))

	eq_(len(binary.code_seg), 4)

	eq_(binary.code_seg[0], 884998144)
	eq_(binary.code_seg[1], 321519616)
	eq_(binary.code_seg[2], 20971562)
	eq_(binary.code_seg[3], 547618816)

def test_Assembler_labels():
	test_string = """
		foo equ 42
		load r1, =foo
		testlabel load r1, =42
		load r2, =testlabel
		load r2, =1
	"""
	asm = Assembler('label test', test_string)
	binary = asm.build_binary()

	eq_(len(binary.code_seg), 4)

	eq_(binary.code_seg[0], binary.code_seg[1])
	eq_(binary.code_seg[2], binary.code_seg[3])

	eq_(binary.symbol_table, {'foo': 42, 'testlabel': 1})

def test_Assembler_data_seg():
	test_string = """
		dc 42
		add r1, r1
		somearray ds 4
		add r2, r2
		somevar dc 4
		add r3, r3
	"""
	asm = Assembler('data seg test', test_string)
	binary = asm.build_binary()

	eq_(len(binary.code_seg), 3)
	eq_(binary.data_seg.to_list(), [42, 0, 0, 0, 0, 4])

	eq_(binary.symbol_table, {'somearray': 4, 'somevar': 8})
