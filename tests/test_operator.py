import unittest
import calligra.operator


class TestBinary(unittest.TestCase):
	def test_array(self):
		op = calligra.operator.array('a', '3')
		self.assertEqual(str(op), 'a[3]')
		op = calligra.operator.array(op, '5')
		self.assertEqual(str(op), 'a[3][5]')
		op = calligra.operator.array('7', op)
		self.assertEqual(str(op), '7[a[3][5]]')

	def test_deref(self):
		op = calligra.operator.deref('a')
		self.assertEqual(str(op), '*a')
		op = calligra.operator.deref(op)
		self.assertEqual(str(op), '*(*a)')

	def test_array_of_deref(self):
		deref = calligra.operator.deref('a')
		array = calligra.operator.array(deref, '3')
		self.assertEqual(str(array), '(*a)[3]')

	def test_deref_of_array(self):
		array = calligra.operator.array('a', '3')
		deref = calligra.operator.deref(array)
		self.assertEqual(str(deref), '*(a[3])')
