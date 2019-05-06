import calligra
import calligra.operator
import calligra.stdlib
import calligra.convert.jansson


class url(calligra.struct):
	def __init__(self, namespace):
		super().__init__(namespace, self.__class__.__name__)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('char'), 'scheme', pointer = True
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('char'), 'authority', pointer = True
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('char'), 'path', pointer = True
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('char'), 'query', pointer = True
		    )
		)
		self.add(
		    calligra.declaration(
		        namespace, namespace.get('char'), 'fragment', pointer = True
		    )
		)


if __name__ == '__main__':
	namespace = calligra.namespace(calligra.stdlib.namespace)
	names = calligra.stdlib.listnames(namespace, url(namespace).type().name())
	types = {name: dict(namespace.get(name)) for name in names}
	code = calligra.stdlib.code(namespace, typesdict = types)
	print(code)
