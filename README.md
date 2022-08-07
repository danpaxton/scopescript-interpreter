# Scope Script Interpreter
View on pypi: https://test.pypi.org/project/scopescript-dpaxton/<br>
View parser: https://github.com/danpaxton/scope-script-parser<br>
View language IDE: https://github.com/danpaxton/scope-script-ide<br>

## Syntax
The interpreter evaluates a program's syntax tree and returns the program output. The syntax tree is represented as a list of statements defined by the following grammar.

### Operators
`type unop ::= !, ~, ++, --, +, -`<br>

`type binop ::= *, /, %, **, +, -, <<, >>, |, &, |, ^, >=, <=, ==, !=, >, <, &&, ||`<br>

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

## Scope