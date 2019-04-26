import unittest
import calligra
import calligra.stdlib
import re


class TestUnion(unittest.TestCase):
	def test_simple(self):
		namespace = calligra.namespace(calligra.stdlib.namespace)
		simple = calligra.union(namespace, 'simple')
		simple.add(
		    calligra.declaration(
		        namespace, namespace.get('size_t'), 'variant1'
		    )
		)
		simple.add(
		    calligra.declaration(namespace, namespace.get('char'), 'variant2')
		)
		code_re = re.compile(
		    r'^union\s+simple\s*{\s*size_t\s+variant1;\s*char\s+variant2;\s*}\s*$'
		)
		self.assertTrue(code_re.match(simple.code()))
		names = calligra.stdlib.listnames(namespace, simple.type().name())
		self.assertEqual(names, ['size_t', 'char', 'union simple'])

	def test_anonymous(self):
		namespace = calligra.namespace(calligra.stdlib.namespace)
		anonymous = calligra.union(namespace, '')
		anonymous.add(
		    calligra.declaration(
		        namespace, namespace.get('size_t'), 'variant1'
		    )
		)
		anonymous.add(
		    calligra.declaration(namespace, namespace.get('char'), 'variant2')
		)
		code_re = re.compile(
		    r'^union\s*{\s*size_t\s+variant1;\s*char\s+variant2;\s*}\s*$'
		)
		self.assertTrue(code_re.match(anonymous.code()))
		with self.assertRaises(KeyError) as cm:
			calligra.stdlib.listnames(namespace, anonymous.type().name())
