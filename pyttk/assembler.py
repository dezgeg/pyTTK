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
ParserElement.enablePackrat()
# error handling rule
rest_of_line = Regex(r'[^\n]+')
opt_whitespace = Optional(Regex(r'[ \t]+'))

def error(msg, allow_empty=True):
	def error_action(s,l,t):
		t['error'] = msg
		t['error_context'] = s.strip()
		t['error_loc'] = l if t else l - 1
		t['error_at_eol'] = len(t) == 0
	if allow_empty:
		return opt_whitespace + (rest_of_line | FollowedBy(LineEnd())).setParseAction(error_action)
	else:
		return opt_whitespace + (rest_of_line + FollowedBy(LineEnd())).setParseAction(error_action)

number = Combine(Optional('-') + Word('0123456789')).setParseAction(
		lambda s,l,t: int(t[0]))

register = MatchFirst([keyword('r' + str(x), x) for x in range(0,7+1)] +
	[keyword('sp', 6), keyword('fp',7)])
opcode = MatchFirst(opcode_generator())
data_op = MatchFirst([keyword(x) for x in ('ds', 'dc', 'equ')])

symbol = ~(register | opcode | data_op) + Word(alphas + '_', alphanums + '_')
address = symbol | number
addrmode_specifier = Literal('=') | Literal('@')
opt_addrmode_specifier = Optional(addrmode_specifier, default=' ')

lparen = Suppress('(')
rparen = Suppress(')') | error("`)'")
### actual rules ###
second_operand = (opt_addrmode_specifier('address_mode') + (register('ri')
				  | (address('imm_value') +
					 Optional(lparen +
					   ((register('ri') + rparen)
						| error('register')))))
				  | (addrmode_specifier + error("`(', register or address"))
				  | error("`@', `=', `(', register or address"))
operands = register('rj') + ((',' + second_operand)
							 | error("`,'", False)
							 | Empty())
operands |= error('register', False)

instruction = opcode('opcode') + Optional(operands)
data_decl = data_op('opcode') + (number('imm_value') | error('integer constant'))

asm_directive = instruction | data_decl
asm_line = Optional(symbol, default='').setParseAction(lambda s,l,t:
	t[0])('label') + asm_directive

asm_line |= symbol + error('opcode or data directive')
asm_line |= error('label, opcode or data directive')
asm_line += Optional(error('end of line', False))

def line_action(s,l,t):
	t['loc'] = l
	return [t]
input_line = (asm_line + OneOrMore(LineEnd().suppress())).setParseAction(line_action)

asm_file = (ZeroOrMore(LineEnd()).suppress() + ZeroOrMore(input_line)).ignore(';' + restOfLine)
### glue code ###
class Assembler:
	def __init__(self, filename, contents):
		self.program = Program()
		self.filename = filename
		self.file_contents = contents.replace("\t", '        ')
		self.parses = asm_file.parseString(self.file_contents, True)
		self.code_seg = []
		self.data_seg = []
		self.data_seg_syms = {}
		self.current_parse = None
		self.errors = []

	def error(self, msg):
		parse = self.current_parse
		error_line = line(parse.loc, self.file_contents)
		error_col = None
		if parse.error_loc != '':
			error_col = col(parse.error_loc, self.file_contents)
			if parse.error_at_eol:
				error_col = len(error_line.rstrip()) + 1
			column_spec = "\n " + error_col * ' ' + '^'
		else:
			column_spec = ""
		self.errors.append("%s:%d%s %s\n> %s%s" %
					 (self.filename, lineno(parse.loc, self.file_contents),
					  (':%s' % error_col) if error_col else '',
					  msg, error_line, column_spec))

	def assign_data_seg_symbol(self, sym):
		self.data_seg_syms[sym] = len(self.data_seg)

	def assign_code_seg_symbol(self, sym):
		self.assign_symbol(sym, len(self.code_seg))

	def assign_symbol(self, sym, value):
		self.program.symbol_table[sym] = value

	def lookup_symbol(self, sym):
		return self.program.symbol_table[sym]

	def append_code_seg(self, insn):
		self.code_seg.append(insn)

	def append_data_seg(self, insn):
		self.data_seg.append(insn)

	def assemble(self):
		parses = self.parses

		for i in parses:
			self.current_parse = i
			if i.error:
				self.error('expecting %s' % (i.error))
			elif i.opcode == 'equ':
				if not i.label:
					self.error('equ without a label')
				else:
					self.assign_symbol(i.label, i.imm_value)
			elif i.opcode == 'dc':
				if i.label:
					self.assign_data_seg_symbol(i.label)
				self.append_data_seg(i.imm_value)
			elif i.opcode == 'ds':
				if i.imm_value < 0:
					self.error("operand to 'ds' must be positive")
				else:
					self.assign_data_seg_symbol(i.label)
					self.data_seg += (0 for _ in xrange(i.imm_value))
			else:
				self.handle_instruction(i)

	def insn_from_parseresult(self, parseresult):
		insn = Insn(parseresult.opcode, 0, 1, 0, 0)

		# Perform validation on operands
		op_flags = Opcodes.opcode_table[parseresult.opcode].flags
		if parseresult.rj == '':
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
		self.assemble()
		cs_size = len(self.code_seg)
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
					insn.imm_value = value
					yield insn.to_binary()

		program = self.program
		program.code_seg = Segment(0, cs_size - 1, code_seg_generator())
		program.data_seg = Segment(cs_size, cs_size + len(self.data_seg) - 1,
				self.data_seg)
		if self.errors:
			return self.errors
		else:
			return program

	def handle_instruction(self, parseresult):
		if parseresult.label:
			self.assign_code_seg_symbol(parseresult.label)

		insn = self.insn_from_parseresult(parseresult)
		self.append_code_seg(insn)
