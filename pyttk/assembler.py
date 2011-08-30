from pyparsing import *

from pyttk.cpu.insn import *
from pyttk.loader.program import *

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

	def insn_from_parseresult(self, parseresult):
		insn = Insn(parseresult.opcode, 0, 1, 0, 0)

		# Perform validation on operands
		op_flags = Opcodes.opcode_table[parseresult.opcode].flags
		if not parseresult.rj:
			if insn.opcode != Opcodes.NOP:
				self.error('instruction requires a first operand')
			return insn

		insn.rj = parseresult.rj
		if not parseresult.address_mode:
			if not op_flags & OpcodeFlags.SND_OPERAND_UNNECESSARY:
				self.error('instruction requires a second operand')
			return insn

		insn.ri = parseresult.ri or Registers.R0
		insn.imm_value = parseresult.imm_value or 0

		is_reg_only = parseresult.address_mode == ' ' and parseresult.imm_value == ''
		if parseresult.opcode == Opcodes.POP and not is_reg_only:
			self.error('second operand to POP must be a register')
			return insn

		# Some instruction require a memory operand as the second operand,
		# their syntax is a bit different
		# See addressing.txt for more info
		if op_flags & OpcodeFlags.SND_OPERAND_MUST_BE_MEMORY:
			if parseresult.address_mode == '=' or is_reg_only:
				self.error('instruction requires a memory operand')
				return insn
			if parseresult.address_mode == '@' and parseresult.imm_value == '':
				# Check for case OP Rj, @Ri
				# XXX: Specified in the manual, but titokone pukes on this
				insn.address_mode = 0
			else:
				insn.address_mode = {' ': 0, '@': 1}[parseresult.address_mode]
		else:
			# check for the case OP Rj, Ri or OP Rj, @Ri
			# should be converted to =0(Ri) and 0(Ri)
			if parseresult.imm_value == '':
				if parseresult.address_mode == '=':
					self.error('OPER Rj, =Ri form not allowed')
					return insn
				insn.address_mode = {' ': AddressModes.IMMEDIATE, '@':
						AddressModes.DIRECT}[parseresult.address_mode]
			else:
				insn.address_mode = {'=': AddressModes.IMMEDIATE,
						' ': AddressModes.DIRECT,
						'@': AddressModes.INDIRECT}[parseresult.address_mode]
		return insn

	def build_binary(self):
		# Assign data segment symbols
		for (sym, value) in self.data_seg_syms.iteritems():
			self.assign_symbol(sym, value + cs_size)

		def code_seg_generator():
			for insn in self.code_seg:
				value = insn.imm_value
				if isinstance(value, basestring):
					value = self.lookup_symbol(value)
				if value is None:
					self.error('undefined symbol', insn)
					yield 0
				elif not Insn.is_valid_immed_value(value):
					self.error('immediate value out of range', insn)
					yield 0
				else:
					yield insn.to_binary()

		program = Program()
		cs_size = len(self.code_seg)
		program.code_seg = Segment(0, cs_size - 1, code_seg_generator())
		program.data_seg = Segment(cs_size, cs_size + len(self.data_seg) - 1,
				self.data_seg)
		return program

	def handle_instruction(self, parseresult):
		if parseresult.label:
			self.assign_code_seg_symbol(parseresult.label)

		insn = self.insn_from_parseresult(parseresult)
		self.append_code_seg(insn)
