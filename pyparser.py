from pyparsing import *

### auxilary instruction parts ###
def keyword(k, v=None):
	parser = CaselessKeyword(k)
	return parser if not v else parser.setParseAction(replaceWith(v))

number = Combine(Optional('-') + Word('0123456789'))

register = Or([keyword('r' + str(x)) for x in range(0,7)] + 
	[keyword('sp', 'r6'), keyword('fp','r7')])
opcode = Or([keyword('add').setName('foo')] + [keyword(x) for x in ('sub', 'pop')])
data_op = Or([keyword(x) for x in ('ds', 'dc', 'equ')])

symbol = ~(register | opcode | data_op) + Regex('[a-zA-Z_][a-zA-Z0-9_]*')
address = symbol | number
addrmode_specifier = Group(Optional(Literal('=') | Literal('@')))
### actual rules ###
second_operand =  addrmode_specifier('address_mode') + (register('ri') |
		(address('imm_value') + Optional('(' + register('ri') + ')')))
operands = register('rj') + Optional(',' + second_operand)
instruction = opcode('opcode') + Optional(operands)
data_decl = data_op('opcode') + address('imm_value')

asm_line = Optional(symbol('label')) + (instruction | data_decl)
line = (asm_line + (LineEnd() | StringEnd())).ignore(';' + restOfLine).setParseAction(
		lambda s,l,t: [t])


asm_file = ZeroOrMore(line)
### glue code ###
class Assembler:
	def __init__(self, filename, contents):
		self.program = Program()
		self.insns = asm_file.parseString(contents)
		self.data_seg = []
		self.data_seg_syms = {}

	def assign_data_seg_symbol(self, sym):
		self.data_seg_syms[sym] = len(data_seg)

	def assign_symbol(self, sym, value):
		self.program.symbol_table[sym] = value

	def run(self):
		insns = self.insns

		for i in insns:
			if i.opcode == 'equ':
				if not i.label:
					self.error(i, 'equ without a label')
				else:
					self.assign_symbol(i.label, i.imm_value)
			elif i.opcode == 'dc':
				self.assign_data_seg_symbol(i.label)
				self.data_seg.append(i.imm_value)
			elif i.opcode == 'ds':
				if i.imm_value < 0:
					self.error(i, "operand to 'ds' must be positive")
				else:
					self.assign_data_seg_symbol(i.label)
					self.data_seg += (0 for _ in xrange(i.imm_value))
			else:
				self.handle_instruction(i)

	def handle_instruction(self, i):
		if i.opcode != Opcodes.NOP and not i.rj:
			self.error(i, 'missing first operand')
			return
testStr = "add r1,r1 ;asdasd \n ; line comment \n foo ds 2 \n sub r1, foo "
for result in asm_file.parseString(testStr, True):

	print 'Label:',  result.label
	print 'Opcode:', result.opcode
	print 'Rj:', result.rj
	print 'Address mode', result.address_mode
	print 'Constant:', result.imm_value
	print 'Ri:', result.ri
	print
