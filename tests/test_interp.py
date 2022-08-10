import os
import sys
import math

test_dir = os.path.dirname( __file__ )
src_dir = os.path.join( test_dir, '..', 'src')
sys.path.append( src_dir )

from scopescript import interpreter as i
from scopescript import atoms as a
from scopescript import scope as s
#Expression tests

def test_boolean():
    assert i.eval_expression(None, {'kind': 'boolean', 'value': False }) == a._boolean(False)

def test_integer():
    assert i.eval_expression(None, {'kind': 'integer', 'value': '-12'}) == a._integer(-12)

def test_float_infinity():
    assert i.eval_expression(None, {'kind': 'float', 'value': 'Infinity'}) == a._float(math.inf)

def test_float_expr():
    assert i.eval_expression(None, {'kind': 'float', 'value': '+12.3241e-21'}) == a._float(+12.3241e-21)
   
def test_string():
    assert i.eval_expression(None, {'kind': 'string', 'value': 'str'}) == a._string('str')

def test_none():
    assert i.eval_expression(None, {'kind': 'null' }) == a._null(None)

def test_variable_top():
    assert i.eval_expression(s.State({ 'x': a._integer(1) }, None, None), {'kind': 'variable', 'name': 'x'}) == a._integer(1)

def test_variable_mid():
    assert i.eval_expression(s.State({}, s.State({}, s.State({ 'x': a._integer(1) }, s.State({} , s.State({ 'x': a._integer(2) }, None, None), None), None), None), None), {'kind': 'variable', 'name': 'x'}) == a._integer(1)

def test_variable_bottom():
    assert i.eval_expression(s.State({}, s.State({}, s.State({ 'y': a._integer(1) }, s.State({} , s.State({ 'x': a._integer(2) }, None, None), None), None), None), None), {'kind': 'variable', 'name': 'x'}) == a._integer(2)

def test_collection_empty():
    assert i.eval_expression(None, {'kind': 'collection', 'value': {}}) == a._collection({})

def test_collection():
    assert i.eval_expression(None, {'kind': 'collection', 'value': { 'a': { 'kind': 'integer', 'value': '1' }, 'b': {'kind': 'integer', 'value': '2' }}}) == a._collection({'a': a._integer(1), 'b':a._integer(2)})

def test_attribute():
    assert i.eval_expression(s.State({ 'x' : a._collection({ 'a': a._integer(1) }) }, None, None), {'kind' : 'attribute', 'collection': {'kind': 'variable', 'name': 'x'}, 'attribute': 'a'}) == a._integer(1)

def test_subscriptor():
    assert i.eval_expression(s.State({ 'x' : a._collection({ '1': a._integer(1) }) }, None, None), {'kind' : 'subscriptor', 'collection': {'kind': 'variable', 'name': 'x'}, 'expr': {'kind': 'integer', 'value': '1'}}) == a._integer(1)

def test_subscriptor_string():
    assert i.eval_expression(None, {'kind' : 'subscriptor', 'collection': {'kind': 'string', 'value': 'str'}, 'expr': {'kind': 'integer', 'value': '1'}}) == a._string('t')

def test_attribute_nested():
    assert i.eval_expression(s.State({ 'x' : a._collection({ 'a': a._collection({ 'b': a._integer(1) }) }) }, None, None), {'kind' : 'attribute', 'collection': {'kind' : 'attribute', 'collection': {'kind': 'variable', 'name': 'x'}, 'attribute': 'a'}, 'attribute': 'b'}) == a._integer(1)

def test_closure_lexical_parent():
    state = {'x': a._integer(1) }
    foo = i.eval_expression(s.State(state, None, None), {'kind': 'closure', 'params': ['a'], 'body': None })
    assert foo.value.env.parent.value is state

def test_logical_not():
    assert i.eval_expression(None, {'kind': 'unop', 'op': '!', 'expr': { 'kind': 'boolean','value': True }}) == a._boolean(False)

def test_bit_not():
    assert i.eval_expression(None, {'kind': 'unop', 'op': '~', 'expr': { 'kind': 'integer','value': '1' }}) == a._integer(-2)

def test_pre_increment():
    scope = { 'x': a._integer(1) }
    assert i.eval_expression(s.State(scope, None, None), {'kind': 'unop', 'op': '++', 'expr': { 'kind': 'variable', 'name': 'x' }}) == a._integer(2)
    assert scope['x'] == a._integer(2)

def test_pre_decrement():
    scope = { 'x': a._integer(1) }
    assert i.eval_expression(s.State(scope, None, None), {'kind': 'unop', 'op': '--', 'expr': { 'kind': 'variable', 'name': 'x' }}) == a._integer(0)
    assert scope['x'] == a._integer(0)

def test_pre_increment_attr():
    scope = ({ 'x': a._collection({ 'a' : a._integer(1) }) })
    assert i.eval_expression(s.State(scope, None, None), {'kind': 'unop', 'op': '++', 'expr': {'kind':'attribute', 'collection': { 'kind': 'variable', 'name': 'x' }, 'attribute': 'a'}}) == a._integer(2)
    assert scope['x'].value['a'] == a._integer(2)

def test_pre_increment_subscriptor():
    scope = { 'x': a._collection({ 'a' : a._integer(1) }) }
    assert i.eval_expression(s.State(scope, None, None), {'kind': 'unop', 'op': '++', 'expr': {'kind':'subscriptor', 'collection': { 'kind': 'variable', 'name': 'x' }, 'expr': {'kind': 'string', 'value': 'a'}}}) == a._integer(2)
    assert scope['x'].value['a'] == a._integer(2)

def test_negation():
    assert i.eval_expression(None, {'kind': 'unop', 'op': '-', 'expr': { 'kind': 'integer','value': '1' }}) == a._integer(-1)

def test_unchanged():
    assert i.eval_expression(None, {'kind': 'unop', 'op': '+', 'expr': { 'kind': 'integer','value': '1' }}) == a._integer(1)

def test_logical_and():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '&&', 'e1': { 'kind': 'integer','value': '1' } , 'e2': {'kind': 'collection', 'value': {} } }) == a._collection({})

def test_logical_or():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '||', 'e1': { 'kind': 'integer','value': '0' } , 'e2': {'kind': 'collection', 'value': {} } }) == a._collection({})

def test_logical_and_shortc():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '&&', 'e1': { 'kind': 'integer', 'value': '0' } , 'e2': None }) == a._integer(0)

def test_logical_or_shortc():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '||', 'e1': { 'kind': 'string', 'value': 'test' } , 'e2': None }) == a._string('test')

def test_concat():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '+', 'e1': { 'kind': 'string','value': 'full' } , 'e2': {'kind': 'string', 'value': 'str' } }) == a._string('fullstr')

def test_plus():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '+', 'e1': { 'kind': 'float','value': '1.1' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._float(2.1)

def test_subtract():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '-', 'e1': { 'kind': 'float','value': '2.5' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._float(1.5)

def test_multiply():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '*', 'e1': { 'kind': 'float','value': '2.5' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._float(2.5)

def test_divide():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '/', 'e1': { 'kind': 'integer','value': '2' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._float(2.0)

def test_remainder():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '%', 'e1': { 'kind': 'integer','value': '2' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._integer(0)

def test_left_shift():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '<<', 'e1': { 'kind': 'integer', 'value': '2' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._integer(4)

def test_right_shift():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '>>', 'e1': { 'kind': 'integer', 'value': '2' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._integer(1)

def test_bit_and():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '&', 'e1': { 'kind': 'integer', 'value': '5' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._integer(1)

def test_bit_or():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '|', 'e1': { 'kind': 'integer', 'value': '5' } , 'e2': {'kind': 'integer', 'value': '-1' } }) == a._integer(-1)

def test_bit_xor():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '^', 'e1': { 'kind': 'integer', 'value': '5' } , 'e2': {'kind': 'integer', 'value': '-1' } }) == a._integer(-6)

def test_equal():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '==', 'e1': { 'kind': 'integer', 'value': '1' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._boolean(True)

def test_not_equal():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '!=', 'e1': { 'kind': 'integer', 'value': '1' } , 'e2': {'kind': 'collection', 'value': {} } }) == a._boolean(True)

def test_less_than():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '<', 'e1': { 'kind': 'integer', 'value': '1' } , 'e2': {'kind': 'integer', 'value': '2' } }) == a._boolean(True)

def test_greater_than():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '>', 'e1': { 'kind': 'string', 'value': 'a' } , 'e2': {'kind': 'string', 'value': 'b' } }) == a._boolean(False)

def test_less_than_eq():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '<=', 'e1': { 'kind': 'integer', 'value': '1' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._boolean(True)

def test_greater_than_eq():
    assert i.eval_expression(None, {'kind': 'binop', 'op': '>=', 'e1': { 'kind': 'integer', 'value': '1' } , 'e2': {'kind': 'integer', 'value': '1' } }) == a._boolean(True)

def test_call_in_place():
    assert i.eval_expression(s.State({}, None, None), {'kind': 'call', 'fun': {'kind': 'closure', 'params': ['a'], 'body': [{'kind': 'return', 'expr': {'kind': 'variable', 'name': 'a'}}]}, 'args': [{'kind': 'integer', 'value': '1'}]}) == a._integer(1)

def test_call_variable():
    parent = s.State({}, None, None)
    parent.value['x'] = a._closure(s.Closure(['a'], [{'kind': 'return', 'expr': {'kind': 'variable', 'name': 'a'}}], parent))
    assert i.eval_expression(parent, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'x'}, 'args': [{'kind': 'integer', 'value': '1'}]}) == a._integer(1)

def test_call_recursive():
    parent = s.State({}, None, None)
    parent.value['foo'] = a._closure(
        s.Closure(['a'], [{'kind': 'if', 
            'truePartArr': [{
                'test': {'kind': 'binop', 'op': '<', 'e1': { 'kind': 'variable', 'name': 'a' } , 'e2': {'kind': 'integer', 'value': '999' } }
                , 'part': [{ 'kind': 'return', 'expr': { 'kind': 'call', 'fun': {'kind': 'variable', 'name': 'foo'}, 'args': [ {'kind': 'binop', 'op': '+', 'e1': { 'kind': 'variable', 'name': 'a' }, 'e2': {'kind': 'integer', 'value': '1'}}]}}]}]
            , 'falsePart': [{'kind': 'return', 'expr': {'kind': 'variable', 'name': 'a'}}]}], parent))

    assert i.eval_expression(parent, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'foo'}, 'args': [{'kind': 'integer', 'value': '0'}] }) == a._integer(999)

def test_call_lexical():
    state = s.State({}, None, None)
    state.value['outer_func'] = a._closure(
        s.Closure(['a'], [{'kind': 'return', 'expr': {'kind': 'closure', 'params': [], 'body': [{'kind': 'return', 'expr': {'kind': 'unop', 'op': '++', 'expr': { 'kind': 'variable', 'name': 'a' }}}]}}], state)
    )
    state.value['inner_func'] = i.eval_expression(state, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'outer_func'}, 'args': [{'kind': 'integer', 'value': '10'}] })
    # inner function remembers lexical environment
    assert i.eval_expression(state, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'inner_func'}, 'args': [] }) == a._integer(11)
    assert i.eval_expression(state, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'inner_func'}, 'args': [] }) == a._integer(12)

def test_ternary_true():
    assert i.eval_expression(None, {'kind': 'ternary', 'test': { 'kind': 'boolean', 'value': True }, 'trueExpr': {'kind': 'integer', 'value': '1' }, 'falseExpr': {'kind': 'integer', 'value': '2' } }) == a._integer(1)

def test_ternary_false():
    assert i.eval_expression(None, {'kind': 'ternary', 'test': { 'kind': 'boolean', 'value': False }, 'trueExpr': {'kind': 'integer', 'value': '1' }, 'falseExpr': {'kind': 'integer', 'value': '2' } }) == a._integer(2)

def test_ternary_sc():
    assert i.eval_expression(None, {'kind': 'ternary', 'test': { 'kind': 'boolean', 'value': False }, 'trueExpr': None, 'falseExpr': {'kind': 'integer', 'value': '2' } }) == a._integer(2)

# Built-in function tests

def test_type():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'type'}, 'args': [{'kind': 'integer', 'value': '1'}]}) == a._string('integer')

def test_ord():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'ord'}, 'args': [{'kind': 'string', 'value': 'a'}]}) == a._integer(ord('a'))

def test_len_collection():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'len'}, 'args': [{'kind': 'collection', 'value': { '1' : { 'kind': 'boolean', 'value': True } } }]}) == a._integer(1)

def test_len_str():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'len'}, 'args': [{'kind': 'string', 'value': 'foo' }]}) == a._integer(3)

def test_pow():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'pow'}, 'args': [{'kind': 'float', 'value': '-3.11111'}, {'kind': 'integer', 'value': '4' }]}) == a._float(pow(-3.11111, 4))
    
def test_bool():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'bool'}, 'args': [{'kind': 'integer', 'value': '1' }]}) == a._boolean(True)

def test_int():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'int'}, 'args': [{'kind': 'float', 'value': '1.11111'}]}) == a._integer(1)
    
def test_int_str():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'int'}, 'args': [{'kind': 'string', 'value': '1'}]}) == a._integer(1)
    
def test_float():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'float'}, 'args': [{'kind': 'integer', 'value': '1'}]}) == a._float(1.0)

def test_float_str():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'float'}, 'args': [{'kind': 'string', 'value': '1.5'}]}) == a._float(1.5)

def test_str():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'str'}, 'args': [{'kind': 'integer', 'value': '1'}]}) == a._string('1')

def test_abs():
    assert i.eval_expression(None, {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'abs'}, 'args': [{'kind': 'integer', 'value': '-1'}]}) == a._integer(1)

def test_print_no_arg():
    res = i.interp_program([{'kind': 'static', 'expr': {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'print'}, 'args': []}}])
    assert res['output'] == ['\n']

def test_print_single_arg():
    res = i.interp_program([{'kind': 'static', 'expr': {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'print'}, 'args': [{'kind': 'string', 'value': 'foo'}]}}])
    assert res['output'] == ['foo', ' ', '\n'] 

def test_print_multiple_arg():
    res = i.interp_program([{'kind': 'static', 'expr': {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'print'}, 'args': [{'kind': 'string', 'value': 'foo'}, {'kind': 'integer', 'value': '1'}]}}])
    assert res['output'] == ['foo', ' ', '1', ' ', '\n']

def test_print_collection():
    res = i.interp_program([{'kind': 'static', 'expr': {'kind': 'call', 'fun': {'kind': 'variable', 'name': 'print'}, 'args': [{'kind': 'collection', 'value': { '1': {'kind': 'integer', 'value': '1'}}}]}}])
    assert res['output'] == ["{'1': 1}", ' ', '\n']

# Statement Tests 

def test_static():
    state = s.State({'x': a._integer(1)}, None, None) 
    i.eval_statement(state, {'kind': 'static', 'expr': {'kind': 'unop', 'op': '++', 'expr': {'kind': 'variable', 'name': 'x'}}}, False)
    assert state.value['x'] == a._integer(2)

def test_assignment_simple():
    state = s.State({}, None, None) 
    i.eval_statement(state, {'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '1'}}, False)
    assert state.value['x'] == a._integer(1)

def test_reassignment():
    state = s.State({'x': a._integer(1)}, None, None) 
    i.eval_statement(state, {'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '2'}}, False)
    assert state.value['x'] == a._integer(2)

def test_assignment_attribute():
    state = s.State({'x': a._collection({})}, None, None) 
    i.eval_statement(state, {'kind': 'assignment', 'assignArr': [{'kind': 'attribute', 'collection': { 'kind':'variable', 'name': 'x'}, 'attribute': 'a'}], 'expr': {'kind': 'integer', 'value': '1'}}, False)
    assert state.value['x'].value['a'] == a._integer(1)

def test_assignment_subscriptor():
    state = s.State({'x': a._collection({})}, None, None)
    i.eval_statement(state, {'kind': 'assignment', 'assignArr': [{'kind': 'subscriptor', 'collection': { 'kind':'variable', 'name': 'x'}, 'expr': { 'kind': 'integer', 'value': '1'}}], 'expr': {'kind': 'integer', 'value': '1'}}, False)
    assert state.value['x'].value['1'] == a._integer(1)

def test_assignment_chain():
    state = s.State({'x': a._collection({})}, None, None) 
    i.eval_statement(state, {'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'z'}, {'kind': 'identifier', 'name': 'y'}, {'kind': 'attribute', 'collection': { 'kind':'variable', 'name': 'x'}, 'attribute': 'a'}], 'expr': {'kind': 'integer', 'value': '1'}}, False)
    assert state.value['z'] == a._integer(1)
    assert state.value['y'] == a._integer(1)
    assert state.value['x'].value['a'] == a._integer(1)

def test_if():
    state = s.State({'x': a._integer(1)}, None, None)
    i.eval_statement(state, {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'boolean', 'value': True}, 'part': [{'kind': 'static', 'expr': {'kind': 'unop', 'op': '--', 'expr': {'kind':'variable', 'name': 'x'}}}]}], 'falsePart': []})
    assert state.value['x'] == a._integer(0)

def test_if_return():
    assert i.eval_statement(s.State({}, None, None), {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'boolean', 'value': True}, 'part': [{'kind': 'return', 'expr': {'kind': 'integer', 'value': '1' }}]}], 'falsePart': []}, i.Flags(True, False)) == ('return', a._integer(1))

def test_else_if():
    state = s.State({'x': a._integer(1)}, None, None)
    i.eval_statement(state, {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'boolean', 'value': False}, 'part': [{'kind': 'static', 'expr': {'kind': 'unop', 'op': '--', 'expr': {'kind':'variable', 'name': 'x'}}}]}, 
        { 'test': {'kind': 'boolean', 'value': True}, 'part': [{'kind': 'static', 'expr': {'kind': 'unop', 'op': '++', 'expr': {'kind':'variable', 'name': 'x'}}}]}], 'falsePart': []})
    assert state.value['x'] == a._integer(2)

def test_else():
    state = s.State({'x': a._integer(1)}, None, None)
    i.eval_statement(state, {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'boolean', 'value': False}, 'part': [{'kind': 'static', 'expr': {'kind': 'integer', 'value': '1'}}]}], 
        'falsePart': [{'kind': 'static', 'expr': {'kind': 'unop', 'op': '++', 'expr': {'kind':'variable', 'name': 'x'}}}]})
    assert state.value['x'] == a._integer(2)

def test_else_return():
    assert i.eval_statement(s.State({}, None, None), {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'boolean', 'value': False}, 'part': []}], 
        'falsePart': [{'kind': 'return', 'expr': {'kind': 'integer', 'value': '1'}}]}, i.Flags(True, False)) == ('return', a._integer(1))

def test_while():
    state = s.State({'x': a._integer(0)}, None, None)
    i.eval_statement(state, {'kind': 'while', 'test': {'kind': 'binop', 'op': '<', 'e1':{'kind': 'variable', 'name':'x'}, 'e2':{'kind': 'integer', 'value': '10'}}, 'body':[{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x'}}}]})
    assert state.value['x'] == a._integer(10) 

def test_while_continue():
    state = s.State({'x': a._integer(0)}, None, None)
    i.eval_statement(state, {'kind': 'while', 'test': {'kind': 'binop', 'op': '<', 'e1':{'kind': 'variable', 'name':'x'}, 'e2':{'kind': 'integer', 'value': '10'}}, 'body':[{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x'}}}, {'kind': 'continue'}, {'kind': 'static', 'expr':{'kind':'unop', 'op':'--', 'expr': { 'kind': 'variable', 'name': 'x'}}}]})
    assert state.value['x'] == a._integer(10) 

def test_while_break():
    state = s.State({'x': a._integer(0)}, None, None)
    i.eval_statement(state, {'kind': 'while', 'test': {'kind': 'boolean', 'value': True }, 'body':[{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x'}}}, {'kind': 'break'}]})
    assert state.value['x'] == a._integer(1) 

def test_while_return():
    state = s.State({'x': a._integer(0)}, None, None)
    assert i.eval_statement(state, {'kind': 'while', 'test': {'kind': 'boolean', 'value': True}, 
    'body':[{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x'}}}
            , {'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'binop', 'op': '==', 'e1': {'kind': 'variable', 'name': 'x'}, 'e2': { 'kind': 'integer', 'value': '10'} }, 'part': [{'kind': 'return', 'expr': {'kind': 'variable', 'name': 'x' }}]}], 'falsePart': []}
            ]}, i.Flags(True, False)) == ('return', a._integer(10))

def test_for():
    state = s.State({'x': a._integer(-5)}, None, None)
    i.eval_statement(state, {'kind': 'for', 
        'inits': [{'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '0'}}]
        , 'test': {'kind': 'binop', 'op': '<', 'e1': {'kind': 'variable', 'name':'x'}, 'e2':{'kind': 'integer', 'value': '10'}}
        , 'updates': [{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x' }}}]
        , 'body':[{'kind': 'static', 'expr':{ 'kind':'integer', 'value':'10' }}]})
    assert state.value['x'] == a._integer(10)

def test_for_return():
    assert i.eval_statement(s.State({}, None, None), {'kind': 'for', 
        'inits': [{'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '0'}}]
        , 'test': {'kind': 'boolean', 'value': True}
        , 'updates': [{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x' }}}]
        , 'body':[{'kind': 'if', 'truePartArr': [{ 'test': {'kind': 'binop', 'op': '==', 'e1': {'kind': 'variable', 'name': 'x'}, 'e2': { 'kind': 'integer', 'value': '10'} }, 'part': [{'kind': 'return', 'expr': {'kind': 'variable', 'name': 'x' }}]}], 'falsePart': []}] }, i.Flags(True, False)) == ('return', a._integer(10))
 
def test_for_break():
    state = s.State({'x': a._integer(-5)}, None, None)
    i.eval_statement(state, {'kind': 'for', 
        'inits': [{'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '0'}}]
        , 'test': {'kind': 'boolean', 'value': True}
        , 'updates': [{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x' }}}]
        , 'body':[{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x'}}}, {'kind': 'break'}] })
    assert state.value['x'] == a._integer(1)

def test_for_continue():
    state = s.State({'x': a._integer(-5)}, None, None)
    i.eval_statement(state, {'kind': 'for', 
        'inits': [{'kind': 'assignment', 'assignArr': [{'kind': 'identifier', 'name': 'x'}], 'expr': {'kind': 'integer', 'value': '0'}}]
        , 'test': {'kind': 'binop', 'op': '<', 'e1': {'kind': 'variable', 'name':'x'}, 'e2':{'kind': 'integer', 'value': '10'}}
        , 'updates': [{'kind': 'static', 'expr':{'kind':'unop', 'op':'++', 'expr': { 'kind': 'variable', 'name': 'x' }}}]
        , 'body':[{'kind': 'continue'}, {'kind': 'static', 'expr':{'kind':'unop', 'op':'--', 'expr': { 'kind': 'variable', 'name': 'x'}}}]})
    assert state.value['x'] == a._integer(10)
    
def test_delete():
    state = s.State({'x': a._collection({'y': a._integer(1)})}, None, None)
    i.eval_statement(state, {'kind': 'delete', 'expr': {'kind': 'attribute', 'collection': {'kind': 'variable', 'name': 'x'}, 'attribute': 'y'}})
    assert 'y' not in state.value['x'].value
    
def test_return():
    assert i.eval_statement(None, {'kind': 'return', 'expr': {'kind': 'integer', 'value': '1'}}, i.Flags(True, False)) == ('return', a._integer(1))
