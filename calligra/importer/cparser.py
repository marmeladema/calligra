import calligra
import calligra.stdlib

import pycparser
import argparse

composite = {
    'Struct': calligra.struct,
    'Union': calligra.union,
    'Enum': calligra.enum,
}


class ASTContext:
	def __init__(self, ns):
		self.namespace = ns
		self.defined = {}


def handle_composite(node, ctx):
	node_name = node.__class__.__name__
	#if not node.name:
	#	raise ValueError(repr(node))
	if node_name in ['Struct', 'Union']:
		#if node.type.decls is not None:
		if node.name and ctx.namespace.has(
		    node_name.lower() + ' ' + node.name
		):
			decl_type = ctx.namespace.get(node_name.lower() + ' ' + node.name)
			if not hasattr(decl_type, 'defined'):
				decl_type.defined = True
			if node.decls is None:
				decl_type.defined |= False
			elif decl_type.defined and decl_type.namespace(
			) is not calligra.stdlib.namespace:
				msg = 'redefinition of \'{}\' at {}'.format(
				    node_name.lower() + ' ' + node.name, node.coord
				)
				raise ValueError(msg)
			else:
				decl_type.defined = True
		else:
			decl_type = composite[node_name](ctx.namespace, node.name)
			decl_type.defined = node.decls is not None

		if node.decls is not None:
			for decl in node.decls:
				child = handle_Decl(decl, ctx)
				decl_type.add(child)

		return decl_type
	elif node_name == 'Enum':
		if node.values:
			decl_type = composite[node_name](ctx.namespace, node.name)
		elif ctx.namespace.has(node_name.lower() + ' ' + node.name):
			decl_type = ctx.namespace.get(node_name.lower() + ' ' + node.name)
		else:
			decl_type = composite[node_name](ctx.namespace, node.type.name)
		return decl_type
	else:
		msg = 'must be Struct, Union or Enum, not {} at {}'.format(
		    node.__class__.__name__, node.coord
		)
		raise TypeError(msg)


def handle_TypeDecl(node, ctx, base = calligra.declaration):
	array = None
	if node.__class__.__name__ == 'ArrayDecl':
		array = node.dim
		node = node.type

	pointer = 0
	while node.__class__.__name__ == 'PtrDecl':
		pointer += 1
		node = node.type

	if node.__class__.__name__ == 'FuncDecl':
		print('[WARN] Unsupported FuncDecl node')
		return
	elif node.__class__.__name__ != 'TypeDecl':
		msg = 'must be TypeDecl, not {} at {}'.format(
		    node.__class__.__name__, node.coord
		)
		raise TypeError(msg)

	if not node.declname:
		msg = 'TypeDecl must have a valid declname, not \'{}\''.format(
		    node.declname
		)
		raise ValueError(msg)

	node_type = node.type.__class__.__name__
	if node_type in ['Union', 'Struct', 'Enum']:
		decl_type = handle_composite(node.type, ctx)
	elif node_type == 'IdentifierType':
		#print(node.quals)
		name = ' '.join(node.type.names)
		decl_type = ctx.namespace.get(name)
	else:
		msg = 'must be IdentifierType, not {} at {}'.format(
		    node_type, node.type.coord
		)
		raise TypeError(msg)

	return base(
	    ctx.namespace,
	    decl_type,
	    node.declname,
	    pointer = pointer,
	    array = array
	)


def handle_Typedef(node, ctx):
	decl = handle_TypeDecl(node.type, ctx)
	if decl is None:
		return
	#if decl.pointer or decl.array or decl.const or decl.volatile or decl.restrict:
	#	msg = 'Unsupported declaration for typedef: {}'.format(dict(decl))
	#	raise ValueError(msg)
	if decl.pointer or decl.array:
		decl = calligra.declaration(
		    ctx.namespace, ctx.namespace.get('uintptr_t'), decl.name()
		)
	try:
		type = ctx.namespace.get(decl.name())
		if type.namespace() is not calligra.stdlib.namespace:
			raise KeyError()
	except KeyError:
		ctx.namespace.register(decl.name(), decl.type())


def handle_Decl(node, ctx):
	if node.funcspec or node.init or node.bitsize:
		msg = 'Unsupported declaration:\n{}\nat {}'.format(
		    repr(node), node.coord
		)
		raise ValueError(msg)

	node_type = node.type.__class__.__name__
	if node_type in ['Struct', 'Union', 'Enum']:
		decl_type = handle_composite(node.type, ctx)
	elif node_type in ['PtrDecl', 'ArrayDecl', 'TypeDecl']:
		return handle_TypeDecl(node.type, ctx)
	elif node_type == 'FuncDecl':
		return handle_TypeDecl(node.type.type, ctx, base = calligra.function)
	else:
		raise TypeError(
		    'must be Struct, Union, not {} at {}'.format(
		        node_type, node.type.coord
		    )
		)

	if node.name:
		return calligra.declaration(ctx.namespace, decl_type, node.name)
	else:
		return decl_type


def handle_FileAST(node, ctx):
	lookup = {
	    'Typedef': handle_Typedef,
	    'Decl': handle_Decl,
	}
	for _, child in node.children():
		handler = lookup.get(child.__class__.__name__, None)
		if handler:
			handler(child, ctx)
		else:
			print(
			    '[WARN] {} node: could not handle {} child node'.format(
			        node.__class__.__name__, child.__class__.__name__
			    )
			)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("file", type=str, help="C file to parse")
	parser.add_argument("-p", "--print", help="Print AST representation", type=str)
	parser.add_argument("--no-cpp", help="Disable preprocessing with cpp", type=bool, default=False)
	args = parser.parse_args()

	ast = pycparser.parse_file(
	    args.file, use_cpp = not args.no_cpp, cpp_args = ['-include', 'pycparser.h']
	)
	if args.print:
		ast.show(buf = open(args.print, 'w+'))
	ctx = ASTContext(calligra.stdlib.namespace)
	handle_FileAST(ast, ctx)
