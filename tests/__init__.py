import unittest
import calligra


class TestPrimaryType(unittest.TestCase):
	def setUp(self):
		self.namespace = calligra.namespace()

	def test_name(self):
		name = 'test'
		primary_type = calligra.PrimaryType(self.namespace, name)
		self.assertEqual(primary_type.name(), name)

	def test_code(self):
		name = 'test'
		primary_type = calligra.PrimaryType(self.namespace, name)
		self.assertEqual(primary_type.code(), name)

	def test_define(self):
		name = 'test1'
		primary_type = calligra.PrimaryType(self.namespace, name)
		self.assertEqual(primary_type.define(), name + ';\n')

		name = 'test2'
		primary_type = calligra.PrimaryType(
		    self.namespace, name, imported = True
		)
		with self.assertRaises(RuntimeError):
			primary_type.define()

	def test_register(self):
		name = 'test'
		primary_type = calligra.PrimaryType(
		    self.namespace, name, register = False
		)
		self.assertEqual(primary_type.register(self.namespace), primary_type)
		self.assertEqual(self.namespace.get(name), primary_type)


class TestNamespace(unittest.TestCase):
	def test_register(self):
		namespace = calligra.namespace()
		name = 'test'
		primary_type1 = calligra.PrimaryType(namespace, name, register = False)

		self.assertEqual(
		    namespace.register(name, primary_type1), primary_type1
		)
		self.assertEqual(namespace.get(name), primary_type1)

		primary_type2 = calligra.PrimaryType(namespace, name, register = False)

		with self.assertRaises(RuntimeError):
			namespace.register(name, primary_type2)


if __name__ == '__main__':
	unittest.main()
