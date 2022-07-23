import collections

State = collections.namedtuple('State', ['value', 'parent'])

# Closure object. Stores function code, parameters, and maintains a link to it's lexical environment.
class Closure:
    def __init__(self, params: list, body: list, parent: State) -> None:
        self.params = params
        self.body = body
        self.env = State({}, parent)

    def __str__(self) -> str:
        return f'<closure at {hex(id(self))}>'
        

# Starts in the current state, follows parent references until variable is found.
def find_in_scope(state: State, name: str) -> tuple | None:
    curr = None
    while state:
        if name in (curr := state.value):
            return curr, curr[name]
        
        state = state.parent

    return None


# Sets the value of a variable in it's own state. Sets value in current state otherwise.
def set_variable(state: State, e: dict, val: tuple) -> tuple:
    name = e['name']; res = find_in_scope(state, name)
    if res:
        res[0][name] = val
    else:
        state.value[name] = val
    
    return val
