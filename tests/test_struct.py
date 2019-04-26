import unittest
import calligra
import calligra.stdlib
import re


class TestStruct(unittest.TestCase):
	def test_simple(self):
		namespace = calligra.namespace(calligra.stdlib.namespace)
		simple = calligra.struct(namespace, 'simple')
		simple.add(
		    calligra.declaration(
		        namespace, namespace.get('size_t'), 'member1'
		    )
		)
		simple.add(
		    calligra.declaration(namespace, namespace.get('char'), 'member2')
		)
		code_re = re.compile(
		    r'^struct\s+simple\s*{\s*size_t\s+member1;\s*char\s+member2;\s*}\s*$'
		)
		self.assertTrue(code_re.match(simple.code()))
		names = calligra.stdlib.listnames(namespace, simple.type().name())
		self.assertEqual(names, ['size_t', 'char', 'struct simple'])

	def test_anonymous(self):
		namespace = calligra.namespace(calligra.stdlib.namespace)
		anonymous = calligra.struct(namespace, '')
		anonymous.add(
		    calligra.declaration(
		        namespace, namespace.get('size_t'), 'member1'
		    )
		)
		anonymous.add(
		    calligra.declaration(namespace, namespace.get('char'), 'member2')
		)
		code_re = re.compile(
		    r'^struct\s*{\s*size_t\s+member1;\s*char\s+member2;\s*}\s*$'
		)
		self.assertTrue(code_re.match(anonymous.code()))
		with self.assertRaises(KeyError) as cm:
			calligra.stdlib.listnames(namespace, anonymous.type().name())
