from collections import namedtuple, deque

# Stores current state and a link to parent state.
State = namedtuple('State', ['value', 'parent', 'output'])

# Stores function code, parameters, and a link to it's lexical environment.
class Closure:
    # Maintains most recent call environment.
    env = deque()
    def __init__(self, params, body, parent) -> None:
        self.params = params
        self.body = body 
        self.parent = parent
    # Push new enviroment state and return it's value.
    def new_env(self) -> dict:
        val = {}
        self.env.append(State(val, self.parent, self.parent.output))
        return val
    # Pop most recently made environment.
    def get_env(self) -> State:
        return self.env.pop()
    

        
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
    name = e['name']
    res = find_in_scope(state, name)
    if res:
        res[0][name] = val
    else:
        state.value[name] = val
    
    return val
