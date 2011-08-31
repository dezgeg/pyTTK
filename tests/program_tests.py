from nose.tools import eq_, ok_
import unittest

from pyttk.loader.program import *

class SegmentTests(unittest.TestCase):

	def test_construct_with_contents(self):
		eq_(len(self.test_seg), 3)
		eq_(self.test_seg.to_list(), [42, -1, 1337])

	def setUp(self):
		self.test_seg = Segment(3, 5, [42, -1, 1337])
		self.zero_seg = Segment(2, 5)

	def test_construct_zeroed(self):
		eq_(len(self.zero_seg), 4)
		eq_(self.zero_seg.to_list(), [0, 0, 0, 0])

	def test_eq(self):
		seg2 = Segment(3, 5, [42, -1, 1337])

		eq_(self.test_seg, seg2)
		ok_(self.test_seg != self.zero_seg)

	def test_iter(self):
		eq_(list(self.test_seg), self.test_seg.to_list())
