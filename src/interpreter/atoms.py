from collections import namedtuple

_boolean=namedtuple('boolean', ['value'])
_integer=namedtuple('integer', ['value'])
_float=namedtuple('float', ['value'])
_string=namedtuple('string', ['value'])
_null=namedtuple('none', ['value'])
_collection=namedtuple('collection', ['value'])
_closure=namedtuple('closure', ['value'])

# Returns tuple name
def kind(val):
    return type(val).__name__

# Number test
def not_number(val: tuple) -> bool:
    res = kind(val)
    return res != 'integer' and res != 'float' and res != 'boolean'

def not_numbers(v1: tuple, v2: tuple) -> bool:
    return not_number(v1) or not_number(v2)

# Integer test
def is_integer(val: tuple) -> bool:
    res = kind(val)
    return res == 'integer' or res == 'boolean'

def not_integers(v1: tuple, v2: tuple) -> bool:
    return not (is_integer(v1) and is_integer(v2))

# Float test
def is_float(val: tuple) -> bool:
    return kind(val) == 'float'

# String test
def is_string(val: tuple) -> bool:
    return kind(val) == 'string'

def are_strings(v1: tuple, v2: tuple) -> bool:
    return is_string(v1) and is_string(v2)

# Float test
def any_floats(v1: tuple, v2: tuple) -> bool:
    return kind(v1) == 'float' or kind(v2) == 'float'

# Subscriptable test
def not_subscriptable(val: tuple) -> bool:
    res = kind(val)
    return res == 'collection' or res == 'closure'

# Collection test
def not_collection(val: tuple) -> bool:
    return kind(val) != 'collection'

# Iterable test
def not_iterable(val: tuple) -> bool:
    res = kind(val)
    return res != 'string' and res != 'collection' 

# Closure test
def not_closure(val: tuple) -> bool:
    return kind(val) != 'closure'

# Maintains the original number type, int or float
def int_or_float(x: tuple, val: int | float) -> tuple:
    return _float(val) if kind(x) == 'float' else _integer(val)

def assignable(val: tuple) -> bool:
    res = kind(val)
    return res == 'variable' or res == 'identifier'
