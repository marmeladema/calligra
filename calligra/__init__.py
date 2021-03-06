import collections
import copy

from . import operator

method_ignored_suffixes = [
    '_t',
]


def method_name(prefix, suffix):
	for ignored_suffix in method_ignored_suffixes:
		if prefix.endswith(ignored_suffix):
			prefix = prefix[:-len(ignored_suffix)]
			break
	prefix = prefix.replace(' ', '_')
	return prefix + suffix


class PrimaryType(object):
	def __init__(
	    self,
	    namespace,
	    name,
	    imported = False,
	    register = True,
	    *args,
	    **kwargs
	):
		self._namespace = namespace
		self._name = name
		self._imported = imported
		super().__init__(*args, **kwargs)

		if register and self.name():
			self.register(namespace)

	@classmethod
	def add_method(cls, name, method):
		setattr(cls, '__method_' + name, method)
		setattr(
		    cls, name,
		    property(
		        fget = lambda self: self.get_method(name),
		        doc = method.__doc__
		    )
		)

	@classmethod
	def methods(cls):
		for attr in dir(cls):
			if attr.startswith('__method_'):
				yield attr[len('__method_'):]

	def get_method(self, name):
		method = getattr(self, '__method_' + name)
		if isinstance(method, type):
			try:
				method = method(self)
			except Exception as e:
				msg = 'Could not initialize method {} of {}'.format(
				    name, self.name()
				)
				raise RuntimeError(msg) from e
			setattr(self, '__method_' + name, method)
		return method

	def type(self):
		return self

	def namespace(self):
		return self._namespace

	def name(self):
		return self._name

	def imported(self):
		return self._imported

	def register(self, ns):
		return ns.register(self.name(), self)

	def define(self):
		if self.imported():
			raise RuntimeError(
			    'could not define imported type %s' % (self.name())
			)
		return self.code() + ';\n'

	def nil(self, ns, chain):
		#if self.type().name() != chain[-1].type().name():
		#	raise RuntimeError('invalid declaration chain',self.name(),chain[-1].type().name())
		return operator.operator('')

	def code(self):
		return self.name()

	def __str__(self):
		return str(self.name())

	def __bool__(self):
		return not self.anonymous()

	def path(self, chain):
		#if self.type().name() != chain[-1].type().name():
		#	raise RuntimeError('invalid declaration chain',self.type().name(),chain[-1].type().name())
		return chain[-1].path(chain[:-1], reference = -1 * chain[-1].pointer)

	def declare(self, namespace, name, *args, **kwargs):
		return declaration(namespace, self.type(), name, *args, **kwargs)

	def __iter__(self):
		yield 'name', self.name()
		yield 'imported', self.imported()
		yield 'methods', list(self.methods())

	def anonymous(self):
		return not self.name()


class ComplexType(PrimaryType):
	def __init__(
	    self, namespace, type, name, register = True, *args, **kwargs
	):
		super().__init__(namespace, name, register = False, *args, **kwargs)
		self._type = type

		if register and name:
			self.register(namespace)

	def code(self):
		return self.type().name()

	def __str__(self):
		return str(self.type())

	def type(self):
		return self._type

	def register(self, ns):
		return ns.register(self.type().name(), self)

	def __iter__(self):
		yield from super().__iter__()
		yield 'type', dict(self.type())


class declaration(ComplexType):
	def __init__(
	    self,
	    namespace,
	    type,
	    name,
	    pointer = False,
	    const = False,
	    volatile = False,
	    restrict = False,
	    array = None,
	    register = False,
	    value = '',
	    *args,
	    **kwargs
	):
		if not str(type):
			raise RuntimeError('could not declare empty type')
		super().__init__(
		    namespace, type, name, register = register, *args, **kwargs
		)
		self._const = const
		self._volatile = volatile
		self._restrict = restrict
		self._pointer = pointer
		self._value = value
		self._array = array

	def name(self, reference = 0, array = 0, prefix = '', suffix = ''):
		if reference < 0:
			prefix = '*' * (-1 * reference) + prefix
			#suffix = ')'
		elif reference > 0:
			prefix = '&' * reference + prefix
		if array:
			suffix += '[%s]' % (array, )
		return prefix + super().name() + suffix

	@property
	def const(self):
		return self._const

	@property
	def volatile(self):
		return self._volatile

	@property
	def restrict(self):
		return self._restrict

	@property
	def pointer(self):
		return self._pointer

	@pointer.setter
	def pointer(self, p):
		if p:
			self._pointer = True
		else:
			self._pointer = False

	@property
	def array(self):
		return self._array

	def code(self, prefix = ''):
		c = ''
		if self.type().anonymous():
			c += super().type().code(prefix = prefix)
		else:
			c += prefix + super().type().type().code()
		if self._const:
			c += ' const'
		if self._volatile:
			c += ' volatile'
		if self._pointer:
			c += ' ' + '*' * int(self._pointer)
		elif self.name():
			c += ' '
		if self._value:
			c += self.assign(self._value)
		else:
			c += self.name(array = self._array if self._array else 0)
		return c

	def nil(self, ns, chain = ()):
		'''
		Is current declaration nil ?
		It does not check if is current declaration is accessible (see self.access)
		'''
		path = self.path(chain)
		cond = operator.operator('')
		if self.pointer:
			cond = operator.eq(path, 'NULL')
		type = self.type()
		if not type.anonymous():
			type = ns.get(type)
		nil = type.nil(ns, chain + (self, ))
		return cond | nil

	def value(self):
		return self._value

	def assign(self, value):
		return self.name() + ' = ' + value

	def access(self, ns, chain):
		'''
		Is current declaration accessible ?
		It does not check if is current declaration is nil (see self.nil)
		'''
		*chain, parent = chain
		if chain:
			access = parent.access(ns, tuple(chain))
		else:
			access = ''
		nil = parent.nil(ns, tuple(chain))
		if nil:
			nil = ~nil
		return access & nil

	def rename(self, name):
		decl = copy.deepcopy(self)
		decl._name = name
		return decl

	def path(self, chain, reference = 0):
		prefix = ''
		suffix = ''
		if chain:
			*chain, parent = chain
			prefix = parent.path(chain, reference = -1 * parent.pointer)
			if parent.pointer:
				prefix = '(' + prefix + ')'
			if parent._array is not None:
				prefix += '['
				suffix = ']'
			else:
				try:
					parent._type.property(self.name())
				except AttributeError as e:
					print(
					    parent, repr(parent.type()), repr(parent._type),
					    repr(parent._type.name()), repr(self._type.name())
					)
					raise e
				prefix += '.'
		return self.name(
		    reference = reference, prefix = prefix, suffix = suffix
		)

	def __iter__(self):
		yield from super().__iter__()
		yield 'const', self.const
		yield 'volatile', self.volatile
		yield 'pointer', self.pointer
		yield 'array', self.array


class typedef:
	def __init__(self, decl):
		self._decl = decl

	def name(self):
		return self._decl.name()

	def __str__(self):
		return 'typedef ' + str(self._decl)


class CompositeType:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._properties = []

	def add(self, decl):
		self._properties.append(decl)

	def properties(self, anonymous = False):
		properties = []
		for property in self._properties:
			if not property.anonymous() or anonymous:
				properties.append(property)
			else:
				properties.extend(property.properties(anonymous = anonymous))
		return tuple(properties)

	def property(self, name):
		properties = self.properties()
		for property in properties:
			if property.name() == name:
				return property
		raise KeyError(
		    'could not find property \'%s\' for type \'%s\'' % (name, self)
		)

	def __iter__(self):
		# pylint: disable=E1101
		yield from super().__iter__()
		yield 'properties', [
		    dict(property) for property in self.properties(anonymous = True)
		]


class function(declaration, CompositeType):
	def __init__(self, namespace, type, name, *args, **kwargs):
		super().__init__(namespace, type, name, *args, **kwargs)

	def body(self, prefix = ''):
		raise NotImplementedError()

	def code(self, body = False):
		s = super().code() + '(' + ', '.join(
		    [p.code() for p in self.properties()]
		) + ')'
		if body:
			s += ' {\n'
			s += self.body(prefix = '\t')
			s += '}\n'
		return s

	def call(self, *args):
		if len(self.properties()) != len(args):
			raise ValueError(
			    "Function %s is expecting %d arguments, not %d" %
			    (self.name(), len(self.properties()), len(args))
			)
		#TODO: check type coherence ?
		#for i in range(0, len(args)):
		#	print(self.properties()[i].name(), self.properties()[i].pointer, args[i].name(), args[i].pointer, self.properties()[i].pointer - args[i].pointer)
		#	print(args[i][-1].path(args[i][:-1], reference = self.properties()[i].pointer - args[i][-1].pointer))
		return self.name() + '(' + ', '.join(
		    [
		        args[i][-1].path(
		            args[i][:-1],
		            reference = self.properties()[i].pointer -
		            (args[i][-1].pointer or args[i][-1].array is not None)
		        ) for i in range(0, len(args))
		    ]
		) + ')'


class NumericType(PrimaryType):
	def __init__(
	    self,
	    *args,
	    min_value = '',
	    max_value = '',
	    format_specifier = '',
	    **kwargs
	):
		super().__init__(*args, **kwargs)
		self._min_value = min_value
		self._max_value = max_value
		self._format_specifier = format_specifier

	def min_value(self):
		return self._min_value

	def max_value(self):
		return self._max_value

	def valid(self, ns, chain):
		min_value = self.min_value()
		if min_value and min_value != ns.get(chain[-1].type().name()
		                                     ).min_value():
			min_value = '%s < %s' % (self.path(chain), min_value)
		else:
			min_value = ''
		max_value = self.max_value()
		if max_value and max_value != ns.get(chain[-1].type().name()
		                                     ).max_value():
			max_value = '%s > %s' % (self.path(chain), max_value)
		if min_value and max_value:
			return min_value + ' || ' + max_value
		elif min_value:
			return min_value
		elif max_value:
			return max_value
		return ''

	@property
	def format_specifier(self):
		return self._format_specifier


class IntegerType(NumericType):
	pass


class RealType(NumericType):
	pass


def add_method(parent, name):
	def _add_method(child):
		parent.add_method(name, child)
		return child

	return _add_method


class struct(CompositeType, ComplexType):
	def __init__(self, namespace, name, *args, **kwargs):
		super().__init__(
		    namespace,
		    PrimaryType(
		        namespace,
		        'struct ' + name if name else 'struct',
		        register = False
		    ), name, *args, **kwargs
		)

	def code(self, prefix = '', body = False):
		c = prefix + self.type().name() + ' {\n'
		for property in self.properties(anonymous = True):
			if property.__doc__:
				c += '\t/** ' + property.__doc__ + ' */\n'
			c += property.code(prefix = prefix + '\t') + ';\n'
		c += prefix + '}'
		return c


@add_method(struct, 'clean')
class struct_clean(function):
	def __init__(self, struct):
		# create function prototype
		namespace = struct._namespace
		name = struct.type().name()
		super().__init__(
		    namespace,
		    namespace.get('void').type(),
		    method_name(namespace.get(name).name(), '_clean')
		)

		self._struct = struct

		self.add(
		    declaration(
		        namespace,
		        self._struct,
		        namespace.get(name).name(),
		        pointer = True
		    )
		)

	def body_prop(self, prop, chain, prefix = ''):
		c = ''

		prop_type = prop.type()

		if hasattr(prop_type, 'clean'):

			if isinstance(prop_type.clean, type):
				prop_type.clean = prop_type.clean(
				    self._namespace,
				    prop.type().name()
				)

			cond = operator.operator('')
			cond &= prop.access(self._namespace, chain)
			cond &= ~prop.nil(self._namespace, chain)
			if cond:
				c += prefix + 'if(%s) {\n' % (cond, )
				prefix += '\t'

			c += prefix + '%s;\n' % (prop_type.clean.call(chain + (prop, )), )
			if prop.pointer:
				c += prefix + 'free(%s);\n' % (prop.path(chain), )
				c += prefix + '%s = NULL;\n' % (prop.path(chain), )

			if cond:
				prefix = prefix[:-1]
				c += prefix + '}\n'
		elif prop_type.anonymous():
			for child in prop_type.properties():
				c += self.body_prop(child, chain + (prop, ), prefix = prefix)

		return c

	def body(self, prefix = ''):
		c = ''
		for prop in self._struct.properties():

			c += self.body_prop(
			    prop, (self.properties()[0], ), prefix = prefix
			)

			prop_type = prop.type()

		return c


class enum(ComplexType, IntegerType, CompositeType):
	def __init__(
	    self, namespace, name, prefix = None, sentinel = None, *args, **kwargs
	):
		super().__init__(
		    namespace,
		    PrimaryType(
		        namespace,
		        'enum ' + name if name else 'enum',
		        register = False
		    ), name, *args, **kwargs
		)
		self._prefix = prefix
		self._sentinel = sentinel

	@property
	def prefix(self):
		return self._prefix

	@property
	def sentinel(self):
		return self._sentinel

	def code(self, prefix = ''):
		c = prefix + self.type().name() + ' {\n'
		for property in self.properties():
			if property.__doc__:
				c += '\t/** ' + property.__doc__ + ' */\n'
			if property.value():
				c += '\t' + property.assign(property.value()) + ',\n'
			else:
				c += '\t' + property.name() + ',\n'
		c += prefix + '}'
		return c


@add_method(enum, 'enum_from_str')
class enum_from_str(function):
	def __init__(self, enum, prefix = None, sentinel = None):
		# create function prototype
		namespace = enum._namespace
		name = enum.type().name()
		super().__init__(
		    namespace,
		    namespace.get(name).type(),
		    method_name(namespace.get(name).name(), '_from_str')
		)
		# add arguments
		self.add(
		    declaration(
		        namespace,
		        namespace.get('char').type(),
		        'str',
		        pointer = True,
		        const = True
		    )
		)
		self._enum = namespace.get(name)
		# prefix filter
		self._prefix = prefix
		if self._prefix is None:
			self._prefix = namespace.get(name).prefix
		# sentinel value
		self._sentinel = sentinel
		if self._sentinel is None:
			self._sentinel = namespace.get(name).sentinel

	# function body, prefix for indetention
	def body(self, prefix = ''):
		c = ''
		for property in self._enum.properties():
			type_name = property.name()
			if type_name.startswith(self._prefix):
				c += prefix + 'if(strcasecmp(str, "{}") == 0) {{\n'.format(
				    type_name[len(self._prefix):]
				)
				c += prefix + '\treturn {};\n'.format(type_name)
				c += prefix + '}\n'
		if self._sentinel:
			c += prefix + 'return ' + self._sentinel + ';\n'
		else:
			c += prefix + 'return 0;\n'
		return c


@add_method(enum, 'enum_to_str')
class enum_to_str(function):
	def __init__(self, enum, prefix = None, sentinel = None):
		# create function prototype
		namespace = enum._namespace
		name = enum.type().name()
		super().__init__(
		    namespace,
		    namespace.get('char').type(),
		    method_name(namespace.get(name).name(), '_to_str'),
		    pointer = True,
		    const = True
		)
		# add arguments
		self.add(
		    declaration(
		        namespace,
		        namespace.get(name).type(),
		        namespace.get(name).name()
		    )
		)
		self._enum = namespace.get(name)
		# prefix filter
		self._prefix = prefix
		if self._prefix is None:
			self._prefix = namespace.get(name).prefix
		# sentinel value
		self._sentinel = sentinel
		if self._sentinel is None:
			self._sentinel = namespace.get(name).sentinel

	# function body, prefix for indetention
	def body(self, prefix = ''):
		c = ''
		c += prefix + 'switch ({}) {{\n'.format(self._enum.name())
		for property in self._enum.properties():
			type_name = property.name()
			if type_name.startswith(self._prefix):
				c += prefix + '\tcase {}:\n'.format(type_name)
				c += prefix + '\t\treturn "{}";\n'.format(
				    type_name[len(self._prefix):]
				)
		c += prefix + '\tdefault: break;\n'
		c += prefix + '}\n'
		c += prefix + 'return NULL;\n'
		return c


class union(CompositeType, ComplexType):
	def __init__(self, namespace, name, *args, **kwargs):
		super().__init__(
		    namespace,
		    PrimaryType(
		        namespace,
		        'union ' + name if name else 'union',
		        register = False
		    ), name, *args, **kwargs
		)

	def code(self, prefix = ''):
		c = prefix + self.type().name() + ' {\n'
		for property in self.properties():
			if property.__doc__:
				c += prefix + '\t/** ' + property.__doc__ + ' */\n'
			c += property.code(prefix = prefix + '\t') + ';\n'
		c += prefix + '}'
		return c


class namespace:
	def __init__(self, parent = None):
		self.types = collections.OrderedDict()
		self.parent = parent

	def register(self, name, type):
		if not isinstance(type, PrimaryType):
			raise ValueError(
			    'type argument should be an instance of PrimaryType'
			)
		if name in self.types and self.types[name] != type:
			raise RuntimeError(
			    'type {} already exists: {}'.format(
			        name, repr(self.types[name])
			    )
			)
		self.types[name] = type
		return type

	def get(self, name):
		name = str(name)
		for t in self.types:
			if str(t) == name:
				return self.types[name]
		if self.parent:
			return self.parent.get(name)
		raise KeyError('unknown type %s' % (name, ))

	def has(self, name):
		try:
			self.get(name)
			return True
		except KeyError:
			return False
