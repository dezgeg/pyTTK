import array
from cpu.insn import Registers
class Cpu:
	def __init__(mem_size, data_seg_size, code_seg):

		# Copy the code segment to the start of memory & fill the rest with zeroes
		self.memory = array.array('L', 
			(code_seg[i] if i < len(code_seg) else 0 for i in xrange(mem_size)))

		# By default, FP points to the last byte in the code segment (wtf?),
		# and SP to end of data segment
		self.registers = [0 for _ in xrange(Registers.NUM_REGS)]
		self.registers[Registers.FP] = len(code_seg) - 1
		self.registers[Registers.SP] = len(code_seg) + data_seg_size - 1

		self.breakpoints = {}

	def get_pc(self):
		""" Get the current value of the Program Counter register """
		return self.registers[Registers.PC]

	def read_mem(self, addr, type='read'):
		if addr < 0 or addr > len(self.memory):
			raise SegFault(addr, type)
		return self.memory[addr]


	def get_index_reg(self, regno):
		"""Returns the current value of the register regno
		used as an index register. By specification, R0 used
		as an index register has the value of 0.
		"""
		assert Registers.is_gpr(regno)
		if regno == Registers.R0:
			return 0
		else:
			return self.registers[regno]
	
	def calculate_insn_ea(self, insn):
	""" Calculate the effective address and operand value of the instruction. """
		if not Opcodes.has_snd_operand(insn.opcode):
			return (None, None)
		if insn.opcode == Opcodes.STORE:
			mem_fetches = insn.address_mode - 1
		else:
			mem_fetches = insn.address_mode

		ea = -1
		ev = insn.imm_value
		for _ in range(mem_fetches):
			ea = ev
			ev = self.read_mem(ev, 'operand fetch')
		return (ea, ev)

	def exec_insn(self, insn):
		(ea, ev) = self.calculate_insn_ea(insn)
		fst_operand = self.get_reg(insn.rj)
		opc = insn.opcode
		opclass = Opcodes.opcode_table[opc][0]

		if opclass == OpcodeClass.ALU:
			if opc == Opcodes.LOAD: result = ev
			elif opc == Opcodes.AND: result = ev & fst_operand
			elif opc == Opcodes.OR: result = ev | fst_operand
			elif opc == Opcodes.XOR: result = ev ^ fst_operand
			elif opc == Opcodes.SHL: result = ev << fst_operand
			elif opc == Opcodes.SHR: result = ev >> fst_operand
			elif opc == Opcodes.SHRA: result = ev >> fst_operand # TODO
			result &= TTK91_INT_MASK
		elif opclass == OpcodeClass.ALU_OVERFLOW_CHECK:
			if opc == Opcodes.ADD: result = ev + fst_operand
			elif opc == Opcodes.SUB: result = ev - fst_operand
			elif opc == Opcodes.MUL: result = ev * fst_operand
			elif opc == Opcodes.DIV: result = ev / fst_operand
			elif opc == Opcodes.MOD: result = ev % fst_operand
			if not TTK91_INT_MIN <= result <= TTK91_INT_MAX:
				raise OverflowFault()
