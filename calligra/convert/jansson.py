import calligra
import calligra.stdlib


@calligra.add_method(calligra.stdlib.boolean, 'to_json')
class boolean_to_json(calligra.function):
	def __init__(self, boolean):
		# create function prototype
		namespace = boolean._namespace
		name = boolean.type().name()
		super().__init__(
		    namespace,
		    namespace.get('json_t').type(),
		    'json_boolean',
		    pointer = True,
		    imported = True,
		)

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		    )
		)


@calligra.add_method(calligra.stdlib.boolean, 'from_json')
class boolean_from_json(calligra.function):
	def __init__(self, boolean):
		# create function prototype
		namespace = boolean._namespace
		name = boolean.type().name()
		super().__init__(
		    namespace,
		    namespace.get('bool').type(),
		    'bool_from_json(',
		)

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = True,
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get('json_t'),
		        'json',
		        pointer = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		code += prefix + 'if(json_is_boolean(json)) {\n'
		code += prefix + '\t*value = json_boolean_value(json);\n'
		code += prefix + '\treturn true;\n'
		code += prefix + '}\n'
		code += prefix + 'return false;\n'
		return code


@calligra.add_method(calligra.IntegerType, 'to_json')
class integer_to_json(calligra.function):
	def __init__(self, integer):
		# create function prototype
		namespace = integer._namespace
		name = integer.type().name()
		super().__init__(
		    namespace,
		    namespace.get('json_t').type(),
		    'json_integer',
		    pointer = True,
		    imported = True,
		)

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		    )
		)


@calligra.add_method(calligra.IntegerType, 'from_json')
class integer_from_json(calligra.function):
	def __init__(self, integer):
		# create function prototype
		namespace = integer._namespace
		name = integer.type().name()
		super().__init__(
		    namespace,
		    namespace.get('bool').type(),
		    name + '_from_json',
		)

		self._integer = integer

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = True,
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get('json_t'),
		        'json',
		        pointer = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		code += prefix + 'if(!json_is_integer(json)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		integer = calligra.declaration(
		    self._namespace, self._namespace.get('json_int_t'), 'integer'
		)
		code += prefix + 'json_int_t integer = json_integer_value(json);\n'
		valid = self._integer.valid(self._namespace, (integer, ))
		if valid:
			code += prefix + 'if({}) {{\n'.format(valid)
			code += prefix + '\treturn false;\n'
			code += prefix + '}\n'
		code += prefix + '*value = ({})integer;\n'.format(self._integer.name())
		code += prefix + 'return true;\n'
		return code


@calligra.add_method(calligra.RealType, 'to_json')
class real_to_json(calligra.function):
	def __init__(self, real):
		# create function prototype
		namespace = real._namespace
		name = real.type().name()
		super().__init__(
		    namespace,
		    namespace.get('json_t').type(),
		    'json_real',
		    pointer = True,
		    imported = True,
		)

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		    )
		)


@calligra.add_method(calligra.RealType, 'from_json')
class real_from_json(calligra.function):
	def __init__(self, real):
		# create function prototype
		namespace = real._namespace
		name = real.type().name()
		super().__init__(
		    namespace,
		    namespace.get('bool').type(),
		    name + '_from_json',
		)

		self._real = real

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = True,
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get('json_t'),
		        'json',
		        pointer = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		code += prefix + 'if(!json_is_real(json)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		real = calligra.declaration(
		    self._namespace, self._namespace.get('double'), 'real'
		)
		code += prefix + 'double real = json_real_value(json);\n'
		code += prefix + 'if({}) {{\n'.format(
		    self._real.valid(self._namespace, (real, ))
		)
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + '*value = ({})real;\n'.format(self._real.name())
		code += prefix + 'return true;\n'
		return code


@calligra.add_method(calligra.stdlib.char, 'to_json')
class char_to_json(calligra.function):
	def __init__(self, char):
		# create function prototype
		namespace = char._namespace
		name = char.type().name()
		super().__init__(
		    namespace,
		    namespace.get('json_t').type(),
		    'json_string',
		    pointer = True,
		    imported = True,
		)

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = True,
		        const = True,
		    )
		)


@calligra.add_method(calligra.stdlib.char, 'from_json')
class char_from_json(calligra.function):
	def __init__(self, char):
		# create function prototype
		namespace = char.namespace()
		name = char.type().name()
		super().__init__(
		    namespace,
		    namespace.get('bool').type(),
		    name + '_from_json',
		)

		self._char = char

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = 2,
		    ),
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get('json_t'),
		        'json',
		        pointer = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		code += prefix + 'if(!json_is_string(json)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + '*value = strndup(json_string_value(json), json_string_length(json));\n'
		code += prefix + 'if(!(*value)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + 'return true;\n'
		return code


@calligra.add_method(calligra.struct, 'to_json')
class struct_to_json(calligra.function):
	def __init__(self, struct):
		# create function prototype
		namespace = struct._namespace
		name = struct.type().name()
		super().__init__(
		    namespace,
		    namespace.get('json_t').type(),
		    namespace.get(name).name() + '_to_json',
		    pointer = True
		)

		self._struct = struct

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        self._struct,
		        namespace.get(name).name(),
		        pointer = True,
		        const = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		properties = self._struct.properties()

		if not properties:
			return code

		code += prefix + 'json_t *json = json_object(), *child;\n'
		code += prefix + 'if(!json) {\n'
		code += prefix + '\treturn NULL;\n'
		code += prefix + '}\n'

		for property in properties:
			property_type = self._namespace.get(property.type().name())

			code += prefix + '/*' + property.name() + '*/\n'
			access = property.access(self._namespace, (self.properties()[0], ))
			nil = property.nil(self._namespace, (self.properties()[0], ))
			if hasattr(property_type, 'to_json'):

				code += prefix + 'if({}) {{\n'.format(access & ~nil)
				code += prefix + '\tchild = {};\n'.format(
				    property_type.to_json.call(
				        (self.properties()[0], property)
				    ),
				)
				code += prefix + '\tif(!child || json_object_set_new_nocheck(json, "{}", child) != 0) {{\n'.format(
				    property.name()
				)
				code += prefix + '\t\tif(child) {\n'
				code += prefix + '\t\t\tjson_decref(child);\n'
				code += prefix + '\t\t}\n'
				code += prefix + '\t\tjson_decref(json);\n'
				code += prefix + '\t\treturn NULL;\n'
				code += prefix + '\t}\n'
				code += prefix + '}\n'

		code += prefix + 'return json;\n'

		return code


@calligra.add_method(calligra.struct, 'from_json')
class struct_from_json(calligra.function):
	def __init__(self, struct):
		# create function prototype
		namespace = struct._namespace
		name = struct.type().name()
		super().__init__(
		    namespace,
		    namespace.get('bool').type(),
		    struct.name() + '_from_json',
		)

		self._struct = struct

		# add arguments
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get(name),
		        'value',
		        pointer = True,
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace,
		        namespace.get('json_t'),
		        'json',
		        pointer = True,
		    )
		)

	def body(self, prefix = ''):
		code = ''
		properties = self._struct.properties()

		if not properties:
			return code

		code += prefix + 'json_t *child;\n'
		code += prefix + 'size_t count = 0;\n\n'
		code += prefix + 'if(!{} || !json_is_object(json)) {{\n'.format(
		    self.properties()[0].name()
		)
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n\n'

		for property in properties:
			property_type = self._namespace.get(property.type().name())

			code += prefix + '/*' + property.name() + '*/\n'
			access = property.access(self._namespace, (self.properties()[0], ))
			#nil = property.nil(self._namespace, (self.properties()[0], ))
			if hasattr(property_type, 'from_json'):

				code += prefix + 'if({}) {{\n'.format(access)
				code += prefix + '\tchild = json_object_get(json, "{}");\n'.format(
				    property.name()
				)
				code += prefix + '\tif(!child) {\n'
				code += prefix + '\t\treturn false;\n'
				code += prefix + '\t}\n'
				child = calligra.declaration(
				    self._namespace,
				    self._namespace.get('json_t'),
				    'child',
				    pointer = True
				)
				code += prefix + '\tif(!{}) {{\n'.format(
				    property_type.from_json.call(
				        (self.properties()[0], property), (child, )
				    ),
				)
				code += prefix + '\t\treturn false;\n'
				code += prefix + '\t}\n'
				code += prefix + '\tcount += 1;\n'
				code += prefix + '}\n'

		code += prefix + 'if(json_object_size(json) != count) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + 'return true;\n'

		return code


@calligra.add_method(calligra.stdlib.in_addr, 'to_json')
class in_addr_to_json(struct_to_json):
	def body(self, prefix = ''):
		code = ''
		code += prefix + 'char str[INET_ADDRSTRLEN] = {0};\n'
		code += prefix + 'if(inet_ntop(AF_INET, {}, str, sizeof(str))) {{\n'.format(
		    self.properties()[0].name()
		)
		code += prefix + '\treturn json_string_nocheck(str);\n'
		code += prefix + '}\n'
		code += prefix + 'return NULL;\n'
		return code


@calligra.add_method(calligra.stdlib.in_addr, 'from_json')
class in_addr_from_json(struct_from_json):
	def body(self, prefix = ''):
		code = ''
		code += prefix + 'const char *str;\n'
		code += prefix + 'if(!json_is_string(json)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + 'str = json_string_value(json);\n'
		code += prefix + 'if(inet_pton(AF_INET, str, {}) == 1) {{\n'.format(
		    self.properties()[0].name()
		)
		code += prefix + '\treturn true;\n'
		code += prefix + '}\n'
		code += prefix + 'return false;\n'
		return code


@calligra.add_method(calligra.stdlib.in6_addr, 'to_json')
class in6_addr_to_json(struct_to_json):
	def body(self, prefix = ''):
		code = ''
		code += prefix + 'char str[INET6_ADDRSTRLEN] = {0};\n'
		code += prefix + 'if(inet_ntop(AF_INET6, {}, str, sizeof(str))) {{\n'.format(
		    self.properties()[0].name()
		)
		code += prefix + '\treturn json_string_nocheck(str);\n'
		code += prefix + '}\n'
		code += prefix + 'return NULL;\n'
		return code


@calligra.add_method(calligra.stdlib.in6_addr, 'from_json')
class in6_addr_from_json(struct_from_json):
	def body(self, prefix = ''):
		code = ''
		code += prefix + 'const char *str;\n'
		code += prefix + 'if(!json_is_string(json)) {\n'
		code += prefix + '\treturn false;\n'
		code += prefix + '}\n'
		code += prefix + 'str = json_string_value(json);\n'
		code += prefix + 'if(inet_pton(AF_INET6, str, {}) == 1) {{\n'.format(
		    self.properties()[0].name()
		)
		code += prefix + '\treturn true;\n'
		code += prefix + '}\n'
		code += prefix + 'return false;\n'
		return code


calligra.PrimaryType(
    calligra.stdlib.namespace, 'json_t', imported = 'jansson.h'
)
calligra.IntegerType(
    calligra.stdlib.namespace,
    'json_int_t',
    imported = True,
    min_value = 'LLONG_MIN',
    max_value = 'LLONG_MAX',
)
