import sys, collections

from scopescript_dpaxton import atoms as a
from scopescript_dpaxton import scope as s

# Depth of 12050 allows no more than 999 recursive calls. Significant overhead.    
sys.setrecursionlimit(12050)

# Flags that indicate if a function is called and if a loop is entered.
Flags = collections.namedtuple('flags', ['in_func', 'in_loop'])

# Terminates program and sets 'output' to the message arg.
def error(state: tuple, msg: str):
    state.output.clear()
    state.output.append(msg)
    assert False

# Expression factory
def expr(f): 
    return lambda state, e: f(state, e)

# Statement factory
def stmt(f):
    return lambda state, s, flags: f(state, s, flags)

# Atom expression functions

# Evaluates null
def _null_(state: s.State, e: dict) -> tuple:
    return a._null(None)

# Evaluates boolean
def _boolean_(state: s.State, e: dict) -> tuple:
    return a._boolean(e['value'])

# Evaluates string
def _string_(state: s.State, e: dict) -> tuple:
    return a._string(e['value'])

# Evaluates integer
def _integer_num_(state: s.State, e: dict) -> tuple:
    return a._integer(int(e['value']))

# Evaluates float
def _float_num_(state: s.State, e: dict) -> tuple:
    return a._float(float(e['value']))

# Evaluates variable
def _variable_(state: s.State, e: dict) -> tuple:
    name = e['name']
    result = s.find_in_scope(state, name)
    if not result:
        error(state, f"Line {e.line}: Variable '{name}' is not defined.")

    return result[1]

# Evaluates collection
def _collection_(state: s.State, e: dict) -> tuple:
    return a._collection({ key: eval_expression(state, val) for key, val in e['value'].items() })

# Evaluates collection
def _closure_(state: s.State, e: dict) -> tuple:
    return a._closure(s.Closure(e['params'], e['body'], state))


# Collection handling

# Determines the attribute of an expression
def determine_attribute(state: s.State, e: dict) -> str | None:
    match e['kind']:
        case 'attribute':
           return e['attribute']
        case 'subscriptor':
            r = eval_expression(state, e['expr'])
            if a.not_subscriptable(r):
                error(state, f"Line {e['line']}: invalid key type for attribute assignment: <{a.kind(r)}>")

            return str(r.value)
    
    return None 

# Handles attribute reference
def _handle_attribute_(state: s.State, e: dict) -> tuple:
    collection = eval_expression(state, e['collection']) 
    if a.not_collection(collection):
        error(state, f"Line {e['line']}: invalid collection type for attribute '{e['attribute']}': <{a.kind(collection)}>")
    
    return collection.value.get(e['attribute'], a._null(None))


# Executes subscriptor on a collection or string, or reports an error
def _handle_subscriptor_(state: s.State, e: dict) -> tuple:
    collection, attribute = eval_expression(state, e['collection']), eval_expression(state, e['expr'])
    if a.not_collection(collection):
        # String indexing
        if a.is_string(collection) and a.is_integer(attribute):
            str_len, index = len(collection.value), attribute.value
            # Error if index is not in range of string length.
            if not -str_len <= index < str_len:
                error(state, f"Line {e['line']}: invalid string index for '{collection.value}': {index}.")
            # Return character as a string.
            return a._string(collection.value[index])

        error(state, f"Line {e['line']}: invalid collection type for attribute '{attribute.value}': <{a.kind(collection)}>.")
    
    if a.not_subscriptable(attribute):
        error(state, f"Line {e['line']}: invalid key type for attribute '{attribute.value}': <{a.kind(attribute)}>.")
 
    return collection.value.get(str(attribute.value), a._null(None))


# Assignment handling

# Assigns collection attribute or variable the argument value.
def assign_val(state: s.State, e: dict, val: tuple) -> tuple | None:
    match e['kind']:
        case 'identifier' | 'variable':
            return s.set_variable(state, e, val)
    
    # Attribute assignment.
    attribute = determine_attribute(state, e)
    # Unknown assignment type.
    if not attribute:
        return None

    collection = eval_expression(state, e['collection']) 
    if a.not_collection(collection):
        error(state, f"Line {e['line']}: invalid collection type for attribute '{attribute}': <{a.kind(collection)}>")

    collection.value[attribute] = val
    return val


# Unary operator functions

# '!'
def _logical_not_(state: s.State, e: dict) -> tuple:
    return a._boolean(not eval_expression(state, e['expr']).value)

# '~'
def _bit_not_(state: s.State, e: dict) -> tuple:
    x = eval_expression(state, e['expr'])
    if not a.is_integer(x):
        error(state, f"Line {e['line']}: invalid operand type for '~': <{a.kind(x)}>.")

    return a._integer(~x.value)

# Prefix increment or decrement
def prefix(state: s.State, e: dict, step: int) -> tuple:
    x, op = eval_expression(state, e['expr']), e['op']
    if a.not_number(x):
            error(state, f"Line {e['line']}: invalid operand type for {op}: <{a.kind(x)}>.")

    res = assign_val(state, e['expr'], a.int_or_float(x, x.value + step)) 
    if not res:
        error(state, f"Line {e['line']}: invalid prefix syntax for {op}: <{a.kind(x)}>.")

    return res

# Unary plus or minus
def plus_minus(state: s.State, e: dict, fact: int) -> tuple:
    x = eval_expression(state, e['expr'])
    if a.not_number(x):
        error(state, f"Line {e['line']}: invalid operand type for {e['op']}: <{a.kind(x)}>.")

    return a.int_or_float(x, x.value * fact) 

# '++'
def _increment_(state: s.State, e: dict) -> tuple:
    return prefix(state, e, 1)

# '--;
def _decrement_(state: s.State, e: dict) -> tuple:
    return prefix(state, e, -1)

# '+'
def _plus_(state: s.State, e: dict) -> tuple:
    return plus_minus(state, e, 1)

# '-'
def _minus_(state: s.State, e: dict) -> tuple:
    return plus_minus(state, e, -1)

# Unary operations
unops = {
    '!': expr( _logical_not_ ),
    '~': expr( _bit_not_ ),
    '++': expr( _increment_ ),
    '--': expr( _decrement_ ),
    '+': expr( _plus_ ),
    '-': expr( _minus_ )
}

# Executes a given unary operation
def _determine_unop_(state: s.State, e: dict) -> tuple:
    op = e['op']
    if op not in unops:
        error(state, f"Line {e['line']}: unknown operator {op}.")
    
    return unops[op](state, e)


# Binary operator functions

# Type checks numeric binary operator operation.
def binop_numeric(state: s.State, e: dict, str=False, float=False):
    e1, e2 = eval_expression(state, e['e1']), eval_expression(state, e['e2'])
    if str and a.are_strings(e1, e2):
        return (lambda val: a._string(val) ), e1.value, e2.value

    if a.not_numbers(e1, e2):
        error(state, f"Line {e['line']}: operator '{e['op']}' not supported between types <{a.kind(e1)}> and <{a.kind(e2)}>.")

    if float or a.any_floats(e1, e2):
        return (lambda val: a._float(val) ), e1.value, e2.value

    return (lambda val: a._integer(val)), e1.value, e2.value

# Type checks bitwise operator operation
def binop_bit(state: s.State, e: dict) -> tuple:
    e1, e2 = eval_expression(state, e['e1']), eval_expression(state, e['e2'])
    if a.not_integers(e1, e2):
        error(state, f"Line {e['line']}: operator '{e['op']}' not supported between types <{a.kind(e1)}> and <{a.kind(e2)}>.")
    
    return e1.value, e2.value

# Type checks comparsion operator operation
def binop_cmp(state: s.State, e: dict) -> tuple:
    e1, e2 = eval_expression(state, e['e1']), eval_expression(state, e['e2'])
    if a.not_numbers(e1, e2) and not a.are_strings(e1, e2):
        error(state, f"Line {e['line']}: operator '{e['op']}' not supported between types <{a.kind(e1)}> and <{a.kind(e2)}>.")
    
    return e1.value, e2.value

# '&&'
def _logical_and_(state: s.State, e: dict) -> tuple:
    e1 = eval_expression(state, e['e1'])
    return e1 if not e1.value else eval_expression(state, e['e2'])

# '||'
def _logical_or_(state: s.State, e: dict) -> tuple:
    e1 = eval_expression(state, e['e1'])
    return e1 if e1.value else eval_expression(state, e['e2'])

# '+'
def _add_concat_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e, str=True)
    return f(v1 + v2)

# '-'
def _subtract_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e)
    return f(v1 - v2)

# '*'
def _multiply_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e)
    return f(v1 * v2)

#'**'
def _exponent_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e)
    return f(v1 ** v2)

# '/' 
def _divide_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e, float=True)
    return f(v1 / v2)

# '%'
def _remainder_(state: s.State, e: dict) -> tuple:
    f, v1, v2 = binop_numeric(state, e)
    return f(v1 % v2)

# '<<'
def _left_shift_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_bit(state, e)
    return a._integer(v1 << v2)

# '>>'
def _right_shift_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_bit(state, e)
    return a._integer(v1 >> v2)

# '&'
def _bit_and_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_bit(state, e)
    return a._integer(v1 & v2)
    
# '|'
def _bit_or_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_bit(state, e)
    return a._integer(v1 | v2)

# '^'
def _bit_xor_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_bit(state, e)
    return a._integer(v1 ^ v2)

# '=='
def _equal_(state: s.State, e: dict) -> tuple:
    e1, e2 = eval_expression(state, e['e1']), eval_expression(state, e['e2'])
    return a._boolean(e1.value == e2.value)

# '!='
def _not_equal_(state: s.State, e: dict) -> tuple:
    e1, e2 = eval_expression(state, e['e1']), eval_expression(state, e['e2'])
    return a._boolean(e1.value != e2.value)

# '<'
def _less_than_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_cmp(state, e)
    return a._boolean(v1 < v2)

# '>'
def _greater_than_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_cmp(state, e)
    return a._boolean(v1 > v2)

# '<='
def _less_than_eq_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_cmp(state, e)
    return a._boolean(v1 <= v2)

# '>='
def _greater_than_eq_(state: s.State, e: dict) -> tuple:
    v1, v2 = binop_cmp(state, e)
    return a._boolean(v1 >= v2)

# Binary operation functions
binops = {
    '&&': expr( _logical_and_ ),
    '||': expr( _logical_or_ ),
    '+': expr( _add_concat_ ),
    '-': expr( _subtract_ ),
    '*': expr( _multiply_ ),
    '**': expr( _exponent_ ), 
    '/': expr( _divide_ ),
    '%': expr( _remainder_ ),
    '<<': expr( _left_shift_ ),
    '>>': expr( _right_shift_ ),
    '&': expr( _bit_and_ ),
    '|': expr( _bit_or_ ),
    '^': expr( _bit_xor_ ),
    '==': expr( _equal_ ),
    '!=': expr( _not_equal_ ),
    '<': expr( _less_than_ ),
    '>': expr( _greater_than_ ),
    '<=': expr( _less_than_eq_ ),
    '>=': expr( _greater_than_eq_ )
}

# Executes a given binary operation.
def _determine_binop_(state: s.State, e: dict) -> tuple:  
    op = e['op']
    if op not in binops:
        error(state, f"Line {e['line']}: unknown operator {op}.")

    return binops[op](state, e)

# Built-in type function, returns type of argument
def _type_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for type(...): {len(args)}.")

    return a._string(a.kind(eval_expression(state, args[0])))

# Built-in ord function, returns the ascii value of the argument
def _ord_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for ord(...): {len(args)}.")

    character = eval_expression(state, args[0])
    if not a.is_string(character):  
        error(state, f"Line {e['line']}: expected a character for ord(...), received <{a.kind(character)}>.")
        
    if len(character.value) != 1:
        error(state, f"Line {e['line']}: expected a character for ord(...), received a string of length {len(character.value)}.")

    return a._integer(ord(character.value))

# Built-in abs function, returns the absoulute value of the number argument.
def _abs_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for abs(...): {len(args)}.")

    number = eval_expression(state, args[0])
    if a.not_number(number):
        error(state, f"Line {e['line']}: invalid argument type for abs(...): <{a.kind(number)}>.")

    return a.int_or_float(number, abs(number.value))

# Built-in len function, returns the number of elements in a collection or string length.      
def _len_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for len(...): {len(args)}.")

    iterable = eval_expression(state, args[0])
    if a.not_iterable(iterable):
        error(state, f"Line {e['line']}: expected a string or collection for len(...), received <{a.kind(iterable)}>.")

    return a._integer(len(iterable.value))

# Built-in bool function, returns the boolean value of the argument.
def _bool_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for bool(...): {len(args)}.")
    
    return a._boolean(bool(eval_expression(state, args[0]).value))

# Built-in int function, returns the greatest integer less than or equal to the argument number.
def  _int_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for int(...): {len(args)}.")

    num = eval_expression(state, args[0])
    # String literal
    if a.is_string(num):
        try:
            return a._integer(int(num.value))
        except:
            error(state, f"Line {e['line']}: invalid literal for int(...) with base 10: '{num.value}'.")

    if a.not_number(num):
        error(state, f"Line {e['line']}: invalid argument type for int(...): <{a.kind(num)}>.")

    return a._integer(int(num.value))
    
# Built-in int function, returns the float representation of the argument number.
def  _float_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for float(...): {len(args)}.")

    num = eval_expression(state, args[0])
    # String literal
    if a.is_string(num):
        try:
            return a._float(float(num.value))
        except:
            error(state, f"Line {e['line']}: could not convert string for float(...): '{num.value}'.")

    if a.not_number(num):
        error(state, f"Line {e['line']}: invalid argument type for float(...): <{a.kind(num)}>.")

    return a._float(float(num.value))


def format_collection(collection) -> str:
    return { k: e.value if a.kind(e) != 'collection' else format_collection(e) for k, e in collection.value.items() }

# Returns string representation of the argument
def str_rep(expr) -> str:
    if a.kind(expr) == 'collection':
        return str(format_collection(expr))
    
    return str(expr.value)

# Built-in str function, returns the string represention of the argument
def _str_(state, e) -> tuple:
    args = e['args']
    if len(args) != 1:
        error(state, f"Line {e['line']}: invalid argument count for str(...): {len(args)}.")
    
    return a._string(str_rep(eval_expression(state, args[0])))

# Prints arguments to output array.
def _print_(state, e) -> tuple:
    out = state.output
    # Append string representation of each argument.
    for arg in e['args']:
        out.append(str_rep(eval_expression(state, arg)) + ' ')

    out.append('\n')
    return a._null(None)
    
# Built-in functions.
built_funcs = {
    'type': expr( _type_ ),
    'ord': expr( _ord_ ),
    'abs': expr( _abs_ ),
    'len': expr( _len_ ),
    'bool': expr( _bool_ ),
    'int': expr( _int_ ),
    'float': expr( _float_ ),
    'str': expr( _str_ ),
    'print': expr( _print_ )
}

# Call Handle.
def _call_(state: s.State, e: dict) -> tuple:
    f = e['fun']

    func_expr, name = None, None
    # Named function.
    if f['kind'] == 'variable':
        name = f['name']
        res = s.find_in_scope(state, name)
        # Named functions override built-in functions.
        if res:
            func_expr = res[1]
        elif name in built_funcs:
            # Return built-in function result.
            return built_funcs[name](state, e)
        else:
            error(state, f"Line {e['line']}: function {name}(...) is not defined.")
    # Anonymous function.
    else:
        func_expr = eval_expression(state, f)

    if a.not_closure(func_expr):
        error(state, f"Line {e['line']}: invalid type for function call: <{a.kind(func_expr)}>.")

    func, args = func_expr.value, e['args']
    # Set name to address if anonymous function.
    if not name:
        name = '(anonymous) func@' + str(hex(id(func)))
    
    if len(args) != len(func.params):
        error(state, f"Line {e['line']}: invalid argument count for {name}(...): Expected {len(func.params)}.")
    # Assign parameters to arguments in the function environment.
    env = func.env.value
    for param, arg in zip(func.params, args):
        env[param] = eval_expression(state, arg)
    # Evaluate function block in it's own environment.
    try:
        result = eval_block(func.env, func.body, Flags(True, False)) 
    except RecursionError:
        error(state, f"Line {e['line']}: maximum recursion depth exceeded for {name}(...).")
    # Return null if there is no return value
    if not result:
        return a._null(None)

    return result[1]


# Ternary handle
def _ternary_(state: s.State, e: dict) -> tuple:
    return eval_expression(state, e['trueExpr']) if eval_expression(state, e['test']).value else eval_expression(state, e['falseExpr'])

# Expressions
expressions = {
    'null': expr( _null_ ),
    'boolean': expr( _boolean_ ),
    'string': expr( _string_ ),
    'integer': expr( _integer_num_),
    'float': expr( _float_num_ ),
    'variable': expr( _variable_ ),
    'collection': expr( _collection_ ),
    'closure': expr( _closure_ ),
    'subscriptor': expr( _handle_subscriptor_ ),
    'attribute': expr( _handle_attribute_ ),
    'unop': expr( _determine_unop_ ),
    'binop': expr( _determine_binop_ ),
    'call': expr( _call_ ),
    'ternary': expr( _ternary_ ),
}

# Evaluates a given expression
def eval_expression(state: s.State, e: dict) -> tuple:
    kind = e['kind']
    if kind not in expressions:
        error(state, f"Line {e['line']}: unknown expression: <{kind}>.") 
    
    return expressions[kind](state, e)


# Statement functions

# Evaluates static statement
def _static_(state: s.State, s: dict, flags: tuple) -> None:
    eval_expression(state, s['expr'])
    return None

# Evaluates assignment statement
def _assignment_(state: s.State, s: dict, flags: tuple) -> None:
    val = eval_expression(state, s['expr'])
    for e in s['assignArr']:
        assign_val(state, e, val)

    return None

# Evaluates if statement
def _if_(state: s.State, e: dict, flags: tuple) -> tuple | None:
    new_state = s.State({}, state, state.output)
    for i in e['truePartArr']:
        if eval_expression(state, i['test']).value:
            return eval_block(new_state, i['part'], flags)
    
    return eval_block(new_state, e['falsePart'], flags)

# Evaluates while statement
def _while_(state: s.State, e: dict, flags: tuple) -> tuple | None:
    new_state = s.State({}, state, state.output)
    new_flags = Flags(flags.in_func, True)

    res = None
    while eval_expression(state, e['test']).value:
        if (res := eval_block(new_state, e['body'], new_flags)):
            match res[0]:
                case 'return' | 'break':
                    return res
                # case 'continue' 

    return None

# Evaluates for statement
def _for_(state: s.State, e: dict, flags: tuple) -> tuple | None:
    new_state = s.State({}, state, state.output)
    for stmt in e['inits']:
        # Flags not required for initializer statements.
        eval_statement(new_state, stmt)

    new_flags = Flags(flags.in_func, True)
    res = None
    while eval_expression(new_state, e['test']).value:
        if (res := eval_block(new_state, e['body'], new_flags)):
            match res[0]:
                case 'return' | 'break':
                    return res
                # case 'continue'

        for stmt in e['updates']:
            # Flags not required for update statements.
            eval_statement(new_state, stmt)
        
    return None

# Evaluates delete statement
def _delete_(state: s.State, e: dict, flags: tuple) -> None:
    expr = e['expr']
    attribute = determine_attribute(state, expr) 
    if not attribute:
        error(state, f"Line {expr['line']}: cannot delete <{expr['kind']}>.")

    collection = eval_expression(state, expr['collection'])
    if a.not_collection(collection):
        error(state, f"Line {expr['line']}: invalid collection type for attribute deletion '{attribute}': <{a.kind(collection)}>.")
    
    if attribute in collection.value:
        del collection.value[attribute]
    else:
        error(state, f"Line {expr['line']}: unknown attribute reference: '{attribute}'.")

    return None 

# Evaluates return statement
def _return_(state: s.State, e: dict, flags: tuple) -> tuple:
    expr = e['expr']
    if not flags.in_func:
        error(state, f"Line {expr['line']}: return outside of function.") 

    return 'return', eval_expression(state, expr)

def _break_(state: s.State, e: dict, flags: tuple) -> tuple:
    if not flags.in_loop:
        error(state, f"Line {e['line']}: break outside of loop.") 

    return 'break', None

def _continue_(state: s.State, e: dict, flags: tuple) -> tuple:
    if not flags.in_loop:
        error(state, f"Line {e['line']}: continue outside of loop.") 

    return 'continue', None

# Statements
statements = {
    'static': stmt( _static_ ),
    'assignment': stmt( _assignment_ ),
    'if': stmt( _if_ ),
    'while': stmt( _while_ ),
    'for': stmt( _for_ ),
    'delete': stmt( _delete_ ),
    'return': stmt( _return_ ),
    'break': stmt( _break_ ),
    'continue':  stmt( _continue_ )
}

# Executes a given ast statement
def eval_statement(state: s.State, e: dict, flags: tuple = Flags(False, False)) -> tuple | None:
    kind = e['kind']
    if kind not in statements:
        error(state, f"Unknown statement: <{kind}>.") 

    return statements[kind](state, e, flags)


# Evaluates a block of code, searches for return value.
def eval_block(state: s.State, b: list, flags: tuple) -> tuple | None:
    ret_val = None
    for stmt in b:
        if (ret_val := eval_statement(state, stmt, flags)):
            break
    
    return ret_val


# Evaluates a program's AST and prdouces an output and final program state.
def interp_program(p):
    out = []
    try:
        eval_block(s.State({}, None, out), p, Flags(False, False))
        return dict(kind='ok', output=out)
    except AssertionError:
        return dict(kind='error', output=out)
    except:
        return dict(kind='error', output=[])