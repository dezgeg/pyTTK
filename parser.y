%token DATA_OP EQU OPCODE NUMBER SYMBOL REGISTER

%%

program: /* empty */
	   | program statement '\n'
	   | program '\n'
	   ;
statement: opt_label DATA_OP address
		 | opt_label instruction
		 | SYMBOL EQU address
		 ; 
opt_label: /* nothing */
		 | SYMBOL
		 ;
address: NUMBER
	   | SYMBOL
	   ;
instruction: OPCODE operands;
operands: /* nothing */
		| REGISTER opt_second_operand
		;
opt_second_operand: /* nothing */
				  | ',' addrmode_specifier snd_operand_tail
				  ;
addrmode_specifier: /* nothing */
				  | '='
				  | '@'
				  ;
snd_operand_tail: address opt_parenregs
				| REGISTER
				;
opt_parenregs: /* nothing */
			 | '(' REGISTER ')'
			 ;
