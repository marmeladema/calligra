import calligra


class boolean(calligra.PrimaryType):
	def __init__(self, namespace):
		super().__init__(namespace, 'bool', imported = True)

	def format_specifier(self):
		return '%u'


class sizeof(calligra.function):
	def __init__(self, namespace):
		super().__init__(
		    namespace,
		    namespace.get('size_t'),
		    self.__class__.__name__,
		    imported = True
		)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('void'), 'type', const = True
		    )
		)


class sa_family_t(calligra.IntegerType):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)

	def nil(self, ns, chain):
		nil = super().nil(ns, chain)
		c = calligra.operator.eq(self.path(chain), 'AF_UNSPEC')
		return nil | c


class in_addr(calligra.struct):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)


class in6_addr(calligra.struct):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)


class timeval(calligra.struct):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)

	def nil(self, ns, chain):
		nil = super().nil(ns, chain)
		path = self.path(chain)
		return nil | (
		    calligra.operator.eq('{}.tv_sec'.format(path), '0') &
		    calligra.operator.eq('{}.tv_usec'.format(path), '0')
		)


class timespec(calligra.struct):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)

	def nil(self, ns, chain):
		nil = super().nil(ns, chain)
		path = self.path(chain)
		return nil | (
		    calligra.operator.eq('{}.tv_sec'.format(path), '0') &
		    calligra.operator.eq('{}.tv_nsec'.format(path), '0')
		)


class char(calligra.PrimaryType):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__, imported = True)

	def nil(self, ns, chain):
		#return 'strlen(%s) == 0' % (self.path(chain),)
		nil = super().nil(ns, chain)
		return nil | calligra.operator.eq(self.path(chain), '0')

	def format_specifier(self):
		return '%s'


@calligra.add_method(char, 'strlen')
class strlen(calligra.function):
	def __init__(self, char):
		name = char.type().name()
		super().__init__(
		    namespace,
		    namespace.get('size_t'),
		    self.__class__.__name__,
		    imported = True
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        's',
		        const = True,
		        pointer = True,
		    )
		)


@calligra.add_method(char, 'clean')
class clean(calligra.function):
	def __init__(self, char):
		super().__init__(
		    namespace, namespace.get('void'), 'memset', imported = True
		)

		self._char = char

		self.add(
		    calligra.declaration(
		        namespace, self._char, 's', pointer = True
		    )
		)
		self.add(
		    calligra.declaration(namespace, namespace.get('uint8_t'), 'c')
		)
		self.add(calligra.declaration(namespace, namespace.get('size_t'), 'n'))

	def call(self, str_arg):
		if isinstance(str_arg[-1].array, str):
			size = '{} - 1'.format(str_arg[-1].array)
		elif str_arg[-1].array:
			size = str(str_arg[-1].array - 1)
		else:
			size = self._char.strlen.call(str_arg)

		c_arg = calligra.declaration(
		    namespace, self._namespace.get('uint8_t'), '0'
		)
		n_arg = calligra.declaration(
		    namespace, self._namespace.get('size_t'), size
		)
		return super().call(str_arg, (c_arg, ), (n_arg, ))


########################################

types = []
namespace = calligra.namespace()

types.append(
    calligra.PrimaryType(namespace, 'void', imported = True).type().name()
)
types.append(
    calligra.IntegerType(
        namespace, 'size_t', min_value = '0', imported = True
    ).type().name()
)
types.append(boolean(namespace).type().name())
types.append(char(namespace).type().name())
types.append(
    calligra.IntegerType(
        namespace,
        'uint8_t',
        min_value = '0',
        max_value = 'UINT8_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'int8_t',
        min_value = 'INT8_MIN',
        max_value = 'INT8_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'uint16_t',
        min_value = '0',
        max_value = 'UINT16_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'int16_t',
        min_value = 'INT16_MIN',
        max_value = 'INT16_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'uint32_t',
        min_value = '0',
        max_value = 'UINT32_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'int32_t',
        min_value = 'INT32_MIN',
        max_value = 'INT32_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace, 'uint64_t', min_value = '0', imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'int64_t',
        min_value = 'INT64_MIN',
        max_value = 'INT64_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'short',
        min_value = 'SHRT_MIN',
        max_value = 'SHRT_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'unsigned short',
        min_value = '0',
        max_value = 'USHRT_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'int',
        min_value = 'INT_MIN',
        max_value = 'INT_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'unsigned int',
        min_value = '0',
        max_value = 'UINT_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'long',
        min_value = 'LONG_MIN',
        max_value = 'LONG_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'unsigned long',
        min_value = '0',
        max_value = 'ULONG_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'long long',
        min_value = 'LLONG_MIN',
        max_value = 'LLONG_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.IntegerType(
        namespace,
        'unsigned long long',
        min_value = '0',
        max_value = 'ULLONG_MAX',
        imported = True
    ).type().name()
)
types.append(
    calligra.RealType(
        namespace,
        'float',
        min_value = 'FLT_MIN',
        max_value = 'FLT_MAX',
        imported = True,
        format_specifier = '%f',
    ).type().name()
)
types.append(
    calligra.RealType(
        namespace,
        'double',
        min_value = 'DBL_MIN',
        max_value = 'DBL_MAX',
        imported = True,
        format_specifier = '%g',
    ).type().name()
)

sizeof(namespace)

types.append(sa_family_t(namespace).type().name())
types.append(in_addr(namespace).type().name())
types.append(in6_addr(namespace).type().name())
types.append(timeval(namespace).type().name())
types.append(timespec(namespace).type().name())


def walk(ns, name, func, visited = None):
	type = ns.get(str(name))
	if visited is None:
		visited = []
	elif type in visited:
		return
	visited.append(type)
	if isinstance(type, calligra.CompositeType):
		for property in type.properties():
			walk(ns, property.type(), func, visited = visited)
	func(type)


def listnames(ns, name):
	names = []
	walk(ns, name, lambda t: names.append(t.type().name()))
	return names


def header(ns, typesdict = {}):
	code = ''

	# declare all types
	code += '/* types declarations */\n'
	for name in typesdict:
		t = ns.get(name)
		if not t.imported():
			if isinstance(t.type(), calligra.enum):
				code += t.define() + '\n'
			else:
				code += t.type().define() + '\n'

	# define all types
	code += '/* types definitions */\n'
	for name in typesdict:
		t = ns.get(name)
		if not t.imported():
			if not isinstance(t.type(), calligra.enum):
				code += t.define() + '\n'

	# declare all functions
	code += '/* functions declarations */\n'
	for name in typesdict:
		t = ns.get(name)
		for method in typesdict[name].get('methods', []):
			func = getattr(t, method)
			if not func.imported():
				code += func.define() + '\n'

	return code


def source(ns, typesdict = {}):
	code = ''

	# define all functions
	code += '/* functions definitions */\n'
	for name in typesdict:
		t = ns.get(name)

		for method in typesdict[name].get('methods', []):
			func = getattr(t, method)
			if not func.imported():
				code += func.code(body = True) + '\n'

	return code


def code(ns, *args, **kwargs):
	code = ''

	code += '/* header */\n'
	code += header(ns, *args, **kwargs)

	code += '/* source */\n'
	code += source(ns, *args, **kwargs)

	return code
