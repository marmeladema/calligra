import unittest
import calligra
import calligra.stdlib
import re


class TestStdlib(unittest.TestCase):
	def test_listnames(self):
		union = calligra.union(calligra.stdlib.namespace, '')
		union.add(
		    calligra.declaration(
		        calligra.stdlib.namespace,
		        calligra.stdlib.namespace.get('size_t'), 'variant1'
		    )
		)
		union.add(
		    calligra.declaration(
		        calligra.stdlib.namespace,
		        calligra.stdlib.namespace.get('char'), 'variant2'
		    )
		)
		simple = calligra.struct(calligra.stdlib.namespace, 'simple')
		simple.add(union)
		names = calligra.stdlib.listnames(
		    calligra.stdlib.namespace,
		    simple.type().name()
		)
		self.assertEqual(names, ['size_t', 'char', 'struct simple'])
