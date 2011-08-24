from pyparsing import *

def keyword(k, v=None):
	return Keyword(k)

number = Combine(Optional('-') + Word('0123456789'))

register = Or([keyword('r' + str(x)) for x in range(0,7)] + 
	[keyword('sp', 'r6'), keyword('fp','r7')])
opcode = Or([keyword('add').setName('foo')] + [keyword(x) for x in ('sub', 'pop')])
data_op = Or([keyword(x) for x in ('ds', 'dc', 'equ')])

comma = Literal(',').suppress()

symbol = ~(register | opcode | data_op) + Regex('[a-zA-Z_][a-zA-Z0-9_]*')
address = symbol | number
### actual rules ###
data_decl = data_op + address
second_operand = Group(Optional(Literal('=') | Literal('@')) + 
		(register | (address + Optional('(' + register + ')'))))
operands = register.setResultsName('rj') + Optional(comma + second_operand)
instruction = opcode.setResultsName('opcode') + Optional(operands)

line = Optional(symbol.setResultsName('label')) + (instruction | data_decl)
line = StringStart() + line.ignore(';' + restOfLine) + StringEnd()

while True:
	inputline = raw_input('> ') + '\n'
	result = line.parseString(inputline)
	print 'Result:', result
	print 'Label:',  result.label
	print 'Opcode:', result.opcode
	print 'Rj:', result.rj
