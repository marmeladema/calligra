import calligra
import calligra.operator
import calligra.stdlib
import calligra.convert.jansson


class network_address(calligra.struct):
	class family(calligra.declaration):
		"""Network address type"""

		def __init__(self, namespace):
			super().__init__(
			    namespace, namespace.get('sa_family_t'),
			    self.__class__.__name__
			)

	class union(calligra.union):
		class ipv4(calligra.declaration):
			"""IPv4 address"""

			def __init__(self, namespace):
				super().__init__(
				    namespace, namespace.get('struct in_addr'),
				    self.__class__.__name__
				)

			def access(self, ns, chain):
				# generate original access condition
				access = super().access(ns, chain)
				# retrieve parent type
				parent = ns.get(chain[-1].type().name())
				# generate path for 'family'
				path = parent.property('family').path(chain)
				# compose '&&' condition based on original condition and 'family' value
				return access & calligra.operator.eq(path, 'AF_INET')

		class ipv6(calligra.declaration):
			"""IPv6 address"""

			def __init__(self, namespace):
				super().__init__(
				    namespace, namespace.get('struct in6_addr'),
				    self.__class__.__name__
				)

			def access(self, ns, chain):
				# generate original access condition
				access = super().access(ns, chain)
				# retrieve parent type
				parent = ns.get(chain[-1].type().name())
				# generate path for 'family'
				path = parent.property('family').path(chain)
				# compose '&&' condition based on original condition and 'family' value
				return access & calligra.operator.eq(path, 'AF_INET6')

		def __init__(self, namespace):
			super().__init__(namespace, '')
			self.add(self.__class__.ipv4(namespace))
			self.add(self.__class__.ipv6(namespace))

	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__)
		self.add(self.__class__.family(namespace))
		self.add(self.__class__.union(namespace))


if __name__ == '__main__':
	names = calligra.stdlib.listnames(
	    calligra.stdlib.namespace,
	    network_address(calligra.stdlib.namespace).type().name()
	)
	types = {name: dict(calligra.stdlib.namespace.get(name)) for name in names}
	code = calligra.stdlib.code(calligra.stdlib.namespace, typesdict = types)
	print(code)
