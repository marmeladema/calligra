import unittest
import calligra.stdlib
import calligra.importer.cparser as cparser
import pycparser
import re

class TestCParserImporter(unittest.TestCase):
	def test_named_decl_with_named_type(self):
		ctx = cparser.ASTContext(calligra.stdlib.namespace)
		code = 'struct test {int member;} test;'
		ast = pycparser.CParser().parse(code, 'stdin')
		self.assertEqual(len(ast.ext), 1)
		decl = calligra.importer.cparser.handle_Decl(ast.ext[0], ctx)

		code_re = re.compile(r'^struct\s+test\s+test$')
		self.assertTrue(code_re.match(decl.code()))

		define_re = re.compile(r'^struct\s+test\s+test;\s*$')
		self.assertTrue(define_re.match(decl.define()))

	def test_named_decl_with_anonymous_type(self):
		ctx = cparser.ASTContext(calligra.stdlib.namespace)
		code = 'struct {int member;} test;'
		ast = pycparser.CParser().parse(code, 'stdin')
		self.assertEqual(len(ast.ext), 1)
		decl = calligra.importer.cparser.handle_Decl(ast.ext[0], ctx)

		code_re = re.compile(r'^struct\s*{\s*int\s+member;\s*}\s*test$')
		self.assertTrue(code_re.match(decl.code()))

		define_re = re.compile(r'^struct\s*{\s*int\s+member;\s*}\s*test;\s*$')
		self.assertTrue(define_re.match(decl.define()))
