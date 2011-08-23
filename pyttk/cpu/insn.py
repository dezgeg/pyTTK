import struct

class OpcodeClass:
	ALU_CHECK_OVERFLOW = 0
	ALU = 1
	BRANCH_ON_RJ = 2
	BRANCH_ON_FLAGS = 3
	SIMULATOR = 4
	OTHER = 5

class Opcodes:
	opcode_table = {}
_optable = [
	# Class 0: ALU 2-operand instructions with overflow checking
	{
		'ADD': 17,
		'SUB': 18,
		'MUL': 19,
		'DIV': 20,
		'MOD': 21,
	},
	# Class 1: ALU 2-operand instructions without overflow checking
	{
		'LOAD': 2,
		'AND': 22,
		'OR': 23,
		'XOR': 24,
		'SHL': 25,
		'SHR': 26,
		'SHRA': 28,
	},
	# Class 2: Jump instructions where the condition is based on the Rj register
	{
		'JUMP': 32,
		'JNEG': 33,
		'JZER': 34,
		'JPOS': 35,
		'JNNEG': 36,
		'JNZER': 37,
		'JNPOS': 38,
	},
	# Class 3: Jump instructions where the condition is based on the flags
	{
		'JLES': 39,
		'JEQU': 40,
		'JGRE': 41,
		'JNLES': 42,
		'JNEQU': 43,
		'JNGRE': 44,
	},
	# Class 4: Simulator affecting instructions
	{
		'IN': 3,
		'OUT': 4,
		'SVC': 112,
	},
	# Class 5: Other instructions
	{
		'NOP': 0,
		'STORE': 1,
		'NOT': 27,
		'COMP': 31,
		'CALL': 49,
		'EXIT': 50,
		'PUSH': 51,
		'POP': 52,
		'PUSHR': 53,
		'POPR': 54,
	}
]
for i in xrange(len(_optable)):
	opgroup = _optable[i]
	for (mnemoic, opcode) in opgroup.iteritems():
		Opcodes.__dict__[mnemoic] = opcode
		Opcodes.opcode_table[opcode] = (i, mnemoic)
_optable = None


class AddressModes:
	IMMEDIATE = 0
	DIRECT = 1
	INDIRECT = 2

class Registers:
	@classmethod
	def is_gpr(cls, regno):
		return regno >= R0 and regno <= R7
	
	R0 = 0
	R1 = 1
	R2 = 2
	R3 = 3
	R4 = 4
	R5 = 5
	R6 = 6
	SP = R6
	R7 = 7
	FP = R7
	FLAGS = 8
	PC = 9

	NUM_REGS = 10

class Svcs:
	HALT = 11
	READ = 12
	WRITE = 13
	TIME = 14
	DATE = 15

class Devices:
	KBD = 0
	CRT = 1

class Insn:
	""" Insn is just a simple immutable container for accessing the operand
	fields in a ttk-91 instruction """

	__slots__ = ('opcode', 'rj', 'address_mode', 'ri', 'imm_value')

	def __init__(self, word):
		(self.opcode, regdata, self.imm_value) = struct.unpack('>BBh', 
			struct.pack('>L', word))
		self.rj = regdata >> 5
		self.address_mode = (0b11000 & regdata) >> 3
		self.ri = regdata & 0b111
	
