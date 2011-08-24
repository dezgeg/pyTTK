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

line = Optional(symbol('label')) + (instruction | data_decl)
line = (line + (LineEnd() | StringEnd())).ignore(';' + restOfLine)

### glue code ###
testStr = "add r1,r1 ;asdasd \n foo ds 2 \n sub r1, foo "
for x in line.scanString(testStr):
	result = x[0]
	print testStr[x[1]:x[2]].rstrip()

	#print 'Result:', result
	print 'Label:',  result.label
	print 'Opcode:', result.opcode
	print 'Rj:', result.rj
	print 'Address mode', result.address_mode
	print 'Constant:', result.imm_value
	print 'Ri:', result.ri
	print
