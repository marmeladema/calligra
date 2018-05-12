class operator(object):
	def __init__(self, symbol):
		self._symbol = symbol

	@property
	def symbol(self):
		return self._symbol

	def __str__(self):
		return self._symbol

	def __len__(self):
		return 0

	def __or__(self, op):
		if self and op:
			return logical_or(self, op)
		elif op:
			return op
		else:
			return self

	def __ror__(self, op):
		return self.__or__(op)

	def __and__(self, op):
		if self and op:
			return logical_and(self, op)
		elif op:
			return op
		else:
			return self

	def __rand__(self, op):
		return self.__and__(op)

	def __invert__(self):
		if self:
			return logical_not(self)
		else:
			return self


class unary(operator):
	def __init__(self, symbol, operand, postfix = False):
		super().__init__(symbol)
		self._operand = operand
		self._postfix = postfix

	def __str__(self):
		symbol = super().__str__()
		operand = str(self._operand)
		if isinstance(self._operand, operator):
			operand = '(' + operand + ')'
		if self._postfix:
			return operand + symbol
		else:
			return symbol + operand

	def __len__(self):
		return 1


class binary(operator):
	def __init__(self, symbol, left, right, associative = False):
		super().__init__(symbol)
		self._left_operand = left
		self._right_operand = right
		self._associative = associative

	def prepare(self, operand):
		s = str(operand)
		if isinstance(operand, binary):
			if not self._associative or self.__class__ != operand.__class__:
				s = '(' + s + ')'
		return s

	def prepare_left(self):
		return self.prepare(self._left_operand)

	def prepare_right(self):
		return self.prepare(self._right_operand)

	@staticmethod
	def build(left, symbol, right):
		return left + ' ' + symbol + ' ' + right

	def __str__(self):
		symbol = super().__str__()

		left_operand = self.prepare_left()
		right_operand = self.prepare_right()

		return self.build(left_operand, symbol, right_operand)

	def __len__(self):
		return 2


class inc(unary):
	def __init__(self, operand):
		super().__init__('++', operand, postfix = False)


class postinc(unary):
	def __init__(self, operand):
		super().__init__('++', operand, postfix = True)


class dec(unary):
	def __init__(self, operand):
		super().__init__('--', operand, postfix = False)


class postdec(unary):
	def __init__(self, operand):
		super().__init__('--', operand, postfix = True)


class ref(unary):
	def __init__(self, operand):
		super().__init__('&', operand, postfix = False)


class deref(unary):
	def __init__(self, operand):
		super().__init__('*', operand, postfix = False)


class logical_not(unary):
	def __init__(self, operand):
		super().__init__('!', operand, postfix = False)

	def __invert__(self):
		return self._operand


class eq(binary):
	def __init__(self, left, right):
		super().__init__('==', left, right, associative = False)

	def __invert__(self):
		return not_eq(self._left_operand, self._right_operand)


class not_eq(binary):
	def __init__(self, left, right):
		super().__init__('!=', left, right, associative = False)

	def __invert__(self):
		return eq(self._left_operand, self._right_operand)


class gt(binary):
	def __init__(self, left, right):
		super().__init__('>', left, right, associative = False)

	def __invert__(self):
		return le(self._left_operand, self._right_operand)


class ge(binary):
	def __init__(self, left, right):
		super().__init__('>=', left, right, associative = False)

	def __invert__(self):
		return lt(self._left_operand, self._right_operand)


class lt(binary):
	def __init__(self, left, right):
		super().__init__('<', left, right, associative = False)

	def __invert__(self):
		return ge(self._left_operand, self._right_operand)


class le(binary):
	def __init__(self, left, right):
		super().__init__('<=', left, right, associative = False)

	def __invert__(self):
		return gt(self._left_operand, self._right_operand)


class logical_and(binary):
	def __init__(self, left, right):
		super().__init__('&&', left, right, associative = True)

	def __invert__(self):
		return (~self._left_operand) | (~self._right_operand)


class logical_or(binary):
	def __init__(self, left, right):
		super().__init__('||', left, right, associative = True)

	def __invert__(self):
		return (~self._left_operand) & (~self._right_operand)


class add(binary):
	def __init__(self, left, right):
		super().__init__('+', left, right, associative = True)


class sub(binary):
	def __init__(self, left, right):
		super().__init__('-', left, right, associative = True)


class mul(binary):
	def __init__(self, left, right):
		super().__init__('*', left, right, associative = True)


class div(binary):
	def __init__(self, left, right):
		super().__init__('/', left, right, associative = True)


class rem(binary):
	def __init__(self, left, right):
		super().__init__('%', left, right, associative = True)


class bitwise_not(unary):
	def __init__(self, operand):
		super().__init__('~', operand, postfix = False)


class array(binary):
	def __init__(self, left, right):
		super().__init__('', left, right, associative = True)

	def prepare_left(self):
		left = self.prepare(self._left_operand)
		if left[0] != '(' and isinstance(
		    self._left_operand, operator
		) and self.__class__ != self._left_operand.__class__:
			left = '(' + left + ')'
		return left

	@staticmethod
	def build(left, symbol, right):
		return left + '[' + right + ']'
