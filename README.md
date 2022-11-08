# DEPRECATED
See https://github.com/danpaxton/scopescript

# ScopeScript Interpreter
View on pypi: https://pypi.org/project/scopescript/<br>
View parser: https://github.com/danpaxton/scopescript-parser<br>
View language IDE: https://github.com/danpaxton/scopescript-ide<br>

## Installation
Clone repository,
```console
$ git clone https://github.com/danpaxton/scopescript-interpreter.git`
$ cd scopescript-interpreter
```
Install and run tests,
```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install pytest
$ pytest
```

Or install package,
```console
$ pip install scopescript
```

## Syntax
The interpreter evaluates a program's syntax tree and returns the program output. The syntax tree is represented as a list of statements defined by the following grammar.

### Operators
`type unop ::= !, ~, ++, --, +, -`<br>

`type binop ::= *, /, %, +, -, <<, >>, |, &, |, ^, >=, <=, ==, !=, >, <, &&, ||`<br>

### Atoms
`type atom ::= { kind: 'null' }`<br>
`| { kind: 'boolean', value: boolean }`<br>
`| { kind: 'integer', value: integer }`<br>
`| { kind: 'float', value: float }`<br>
`| { kind: 'string', value: string }`<br>
`| { kind: 'collection', value: { [ key: string ]: [ value: expression ] } }`<br>
`| { kind: 'variable', name: name }`<br>
`| { kind: 'closure', params: name[], body: Stmt[] }`<br>

### Expressions
`type expression ::= atom`<br>
`| { kind: 'unop', op: unop, expr: expression }`<br>
`| { kind: 'binop', op: binop, e1: expression, e2: expression }`<br>
`| { kind: 'call', fun: expression, args: expression[] }`<br>
`| { kind: 'subscriptor', dict: expression, expression: expression }`<br>
`| { kind: 'attribute', dict: expression, attribute: name }`<br>
`| { kind: 'ternary', test: expression, trueExpr: expression, falseExpr: expression }`<br>

### Statements
`type statement ::= { kind: 'static', expr: expression }`<br>
`| { kind: 'assignment', assignArr: expression[], expr: expression }`<br>
`| { kind: 'if', truePartArr : { test: expression, part: statement[] }[], falsePart: statement[] }`<br>
`| { kind: 'for', inits: statement[], test: expression, updates: statement[], body: statement[] }`<br>
`| { kind: 'while', test: expression, body: statement[]] }`<br>
`| { kind: 'delete', expr: expression }`<br>
`| { kind: 'return', expr: expression }`<br>
`| { kind: 'break' }`<br>
`| { kind: 'continue' }`<br>

## Scope
Program scope is represented as a linked list of states. Each state is represented as a python namedtuple with value, parent, and output attributes. The value attribute points to a dictionary containing the state's local variables and their mappings. The parent attribute points to the outer-state relative to itself. Lastly, the output attribute points to the program output list. Variable look up starts in the current state and follows parents pointers to find variables that are global to the current state. At any point in the program, the only variables that can be referenced must be on the path from the current state to the outermost state.

## Closures
Closures are represented as an object with params, body, parent and env attributes. The params attribute stores a list of strings that represent each parameter. The body attribute stores a block of code to be executed on call. The parent attribute maintains a link to it's creating state at closure creation time. Lastly, the env attribute is a python deque that tracks the most recently made call environment. Variable look up during a function call follows the closure's lexical enivronment, not the current program scope.

## Interpreter
The interpreter is built using a network of python dictionaries containing function factories. The main two dictionaries that drive decision making are the statements and expressions dictionaries. The statements dictionary receives a statement node and creates the desired function for the statement kind. The expressions dictionary receives an expression node and creates the desired function for the expression kind. Statement nodes point to other statement nodes (self-referencing) or expression nodes. Once the program is operating using the expressions dictionary the only way to operate on the statements dictionary again would be through a function call, otherwise there is only access to the expressions dictionary from expression nodes. There also exists helper dictionaries for operator and built-in function use, both are used by the expressions dictionary. Programs and function blocks are both represented as a list of statement nodes that the interpreter sequentially evaluates.

## Additional language information
https://github.com/danpaxton/scopescript-parser/blob/main/README.md
