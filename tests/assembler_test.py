from nose.tools import(eq_, ok_)
import unittest

from pyttk.cpu.insn import Opcodes
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

