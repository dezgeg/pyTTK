from pyparsing import *

from pyttk.cpu.insn import *
from pyttk.loader.program import Program

### auxilary instruction parts ###
def keyword(k, v=None):
	parser = CaselessKeyword(k)
	return parser if v is None else parser.setParseAction(replaceWith(v))

def opcode_generator():
	for opcode,opdata in Opcodes.opcode_table.iteritems():
		yield keyword(opdata[1], opcode)

ParserElement.setDefaultWhitespaceChars(" \t")

number = Combine(Optional('-') + Word('0123456789')).setParseAction(
		lambda s,l,t: int(t[0]))

register = Or([keyword('r' + str(x), x) for x in range(0,7+1)] + 
	[keyword('sp', 6), keyword('fp',7)])
opcode = Or(opcode_generator())
data_op = Or([keyword(x) for x in ('ds', 'dc', 'equ')])

symbol = ~(register | opcode | data_op) + Word(alphas + '_', alphanums + '_')
address = symbol | number
addrmode_specifier = Optional(Literal('=') | Literal('@'), default=' ')
### actual rules ###
second_operand =  addrmode_specifier('address_mode') + (register('ri') |
		(address('imm_value') + Optional(
			Suppress('(') + register('ri') + Suppress(')'))))
operands = register('rj') + Optional(Suppress(',') + second_operand)
instruction = opcode('opcode') + Optional(operands)
data_decl = data_op('opcode') + number('imm_value')

asm_line = Optional(symbol, default='').setParseAction(lambda s,l,t:
	t[0])('label') + (instruction | data_decl)
line = (asm_line + OneOrMore(LineEnd().suppress())).setParseAction(
		lambda s,l,t: [t])

asm_file = (ZeroOrMore(LineEnd()).suppress() + ZeroOrMore(line)).ignore(';' + restOfLine)
### glue code ###
class Assembler:
	def __init__(self, filename, contents):
		self.program = Program()
		self.insns = asm_file.parseString(contents)
		self.code_seg = []
		self.data_seg = []
		self.data_seg_syms = {}

	def assign_data_seg_symbol(self, sym):
		self.data_seg_syms[sym] = len(data_seg)

	def assign_symbol(self, sym, value):
		self.program.symbol_table[sym] = value

	def append_code_seg(self, insn):
		self.code_seg.append(insn)

	def assemble(self):
		insns = self.insns

		for i in insns:
			if i.opcode == 'equ':
				if not i.label:
					self.error(i, 'equ without a label')
				else:
					self.assign_symbol(i.label, i.imm_value)
			elif i.opcode == 'dc':
				self.assign_data_seg_symbol(i.label)
				self.append_data_seg(i.imm_value)
			elif i.opcode == 'ds':
				if i.imm_value < 0:
					self.error(i, "operand to 'ds' must be positive")
				else:
					self.assign_data_seg_symbol(i.label)
					self.data_seg += (0 for _ in xrange(i.imm_value))
			else:
				self.handle_instruction(i)

	def handle_instruction(self, i):
		if i.label:
			self.assign_code_seg_symbol(i.label)
		(address_mode, imm_value, ri) = (i.address_mode, i.imm_value, i.ri)

		# Perform validation on operands
		if not i.rj:
			if i.opcode != Opcodes.NOP:
				self.error(i, 'missing first operand')
				return
			else: # Fill unused fields with zeroes
				rj = 0
				address_mode = '='
		op_flags = Opcodes.opcode_table[i.opcode]

		if not address_mode:
			if not op_flags.flags & OpcodeFlags.SND_OPERAND_UNNECESSARY:
				self.error(i, 'instruction requires a second operand')
				return
			else:
				address_mode = '='

		# check for the case OP Rj, Ri or OP Rj, @Ri
		# should be converted to =0(Ri) and 0(Ri)
		if imm_value == '':
			if address_mode == ' ':
				address_mode = '='
			elif address_mode == '@':
				address_mode = ' '
			else:
				pass # TODO: is =Ri form allowed???
		ri = ri or Registers.R0
		imm_value = imm_value or 0
		address_mode = {'=': AddressModes.IMMEDIATE,
				' ': AddressModes.DIRECT,
				'@': AddressModes.INDIRECT}[address_mode]

		self.append_code_seg(Insn(i.opcode, i.rj or 0, address_mode, ri,
			imm_value))
