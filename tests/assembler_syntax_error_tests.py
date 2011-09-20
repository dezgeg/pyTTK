import unittest
from nose.tools import eq_, ok_

from pyttk.assembler import Assembler

def assertExpected(s, loc, msgs):
    res = Assembler('test.k91', s).build_binary()
    print res
    ok_(len(res) == 1)
    ok_(res[0].startswith('test.k91:1:%d' % loc))
    ok_('expecting' in res[0])
    for msg in msgs:
        if msg[0] == '!':
            try:
                res[0].index(msg[1:])
                self.fail()
            except ValueError:
                pass
        else:
            ok_(res[0].index(msg), msg)

class Assembler_syntax_error_tests(unittest.TestCase):
    def test_error_at_start_of_line(self):
        assertExpected('12345 add r1, r2', 1, ['label', 'opcode', 'data directive'])

    def test_error_after_label(self):
        assertExpected('foo quux', 5, ['!label', 'opcode', 'data directive'])

    def test_error_after_data_op(self):
        assertExpected('foo ds !!!', 8, ['integer constant'])

    def test_mismatched_paren(self):
        assertExpected('add r1, asd(r2', 15, ["`)'"])

    def test_error_after_comma(self):
        errors = ["`('", "`@'", "`='", "address", "register"]
        assertExpected('add r1,', 8, errors)
        assertExpected('add r1, ?', 9, errors)

    def test_error_after_paren(self):
        assertExpected('add r1, foo(asd)', 13, ['!address', 'register'])

    def test_error_after_opcode(self):
        assertExpected('add foo', 5, ['register'])

    def test_error_after_first_operand(self):
        assertExpected('add r1 asd', 8, ["`,'"])

    def test_error_after_addrmode_specifier(self):
        assertExpected('add r1, ==0', 10, ["`('", "address", "register"])

    def test_error_after_end_of_instruction(self):
        assertExpected('sub r2, @foo(r2) asdasd', 18, ["end of line"])
