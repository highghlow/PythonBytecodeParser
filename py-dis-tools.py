import dis

class AbstractObject:
    def __init__(self):
        self.modified_attrs : dict[str, AbstractObject] = dict()
    def set_attr(self, attr, val):
        self.modified_attrs[attr] = val
    def get_attr(self, attr):
        return self.modified_attrs.get(attr, Unknown())
    def remove_modified_attr(self, attr):
        del self.modified_attrs[attr]

class Unknown(AbstractObject):
    pass

class UnknownName(AbstractObject):
    def __init__(self, name : str):
        self.name = name
        
        super().__init__()
    def __repr__(self) -> str:
        return f"unknown-name({self.name}, modifications: {self.modified_attrs})"

class Value(AbstractObject):
    def __init__(self, value) -> None:
        self.value = value

        super().__init__()
    def __repr__(self) -> str:
        return f"value({self.value}, modifications: {self.modified_attrs})"

class Attribute(AbstractObject):
    def __init__(self, attr_of : AbstractObject, name : str, value : AbstractObject) -> None:
        self.of = attr_of
        self.name = name
        self.value = value

        super().__init__()
    def __repr__(self) -> str:
        return f"attribute({self.of}.{self.name} = {self.value}, modifications: {self.modified_attrs})"

class Module(AbstractObject):
    def __init__(self, name : str) -> None:
        self.name = name

        super().__init__()
    def __repr__(self) -> str:
        return f"module({self.name}, modifications: {self.modified_attrs})"

class BuiltIn(AbstractObject):
    def __init__(self, name : str) -> None:
        self.name = name

        super().__init__()
    def __repr__(self) -> str:
        return f"builtin({self.name}, modifications: {self.modified_attrs})"

class Call(AbstractObject):
    def __init__(self, func : AbstractObject, args : list[AbstractObject], kwargs : dict[str, AbstractObject] ={}) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

        super().__init__()
    def __repr__(self) -> str:
        return f"call({self.func}, {', '.join(str(i) for i in self.args)}, {', '.join(f'{k, v}' for k, v in self.kwargs.items())}, modifications: {self.modified_attrs})"

class Operation(AbstractObject):
    def __init__(self, op : str, obj1 : AbstractObject, obj2 : AbstractObject | None = None):
        self.obj1 = obj1
        self.obj2 = obj2
        self.op = op
        
        super().__init__()
    def __repr__(self) -> str:
        return f"operation({self.obj1} {self.op} {self.obj2})"

class Compare(AbstractObject):
    def __init__(self, comp : str, obj1 : AbstractObject, obj2 : AbstractObject):
        self.obj1 = obj1
        self.obj2 = obj2
        self.comp = comp
        
        super().__init__()
    def __repr__(self) -> str:
        return f"compare({self.obj1} {self.comp} {self.obj2})"

class Outcome:
    def __init__(self, conditions : list[AbstractObject], outcome : AbstractObject) -> None:
        self.conditions = conditions
        self.outcome = outcome
    def __repr__(self) -> str:
        return f"outcome({' && '.join(str(i) for i in self.conditions)} -> {self.outcome})"

class PossibleOutcomes(AbstractObject):
    def __init__(self, outcomes : list[Outcome], else_outcome : AbstractObject | None = None) -> None:
        self.outcomes = outcomes
        self.else_outcome = else_outcome
    def add_outcome(self, outcome : Outcome):
        self.outcomes.insert(0, outcome)
    def __repr__(self) -> str:
        return f"possibility({', '.join(str(i) for i in self.outcomes)}{f', else -> {self.else_outcome}' if self.else_outcome != None else ''})"

class Jump:
    def __init__(self, condition : AbstractObject, destination : int) -> None:
        self.condition = condition
        self.destination = destination
    def __repr__(self) -> str:
        return f"jump({self.condition} -> {self.destination})"

source_full = '''

# load constants onto the stack
constant_int = 42
constant_float = 2.71828
constant_str = "hello, world!"
constant_bytes = b'\\x00\\x01\\x02'
constant_tuple = (1, 2, 3)

# store a variable
local_var = a + b

# control flow statements
if a > b:
    print("a is greater than b")
elif a < b:
    print("a is less than b")
else:
    print("a and b are equal")

while a < 10:
    a += 1

for i in range(10):
    print(i)

# function call and return
def add(x, y):
    return x + y

result = add(a, b)

# binary operations
sum = a + b
difference = a - b
product = a * b
quotient = a / b
modulo = a '''+"%"+''' b

# compare values
equal_check = (a == b)
not_equal_check = (a != b)
greater_check = (a > b)
less_check = (a < b)

# logical operations
and_check = (a > b) and (b > 0)
or_check = (a > b) or (b < 0)
not_check = not (a > b)

# attribute access and method call
string_length = len(constant_str)
list_obj = [1, 2, 3]
list_length = len(list_obj)
list_obj.append(4)

# exceptions and errors
try:
    num = int("not a number")
except ValueError:
    print("invalid literal for int()")

assert a == b, "a and b are not equal"

'''

source_basic_if = '''
a = 0
if b > 0 or b != 2:
    a = 1
print(a)
'''

comp = compile(source_basic_if, "test", "exec")

stack = []
calls = []
names = {
    "print" : BuiltIn("print")
}

active_jumps = []

kw_names = 0

bytecode = dis.Bytecode(comp)
constants = bytecode.codeobj.co_consts
print(bytecode.dis())

BASE_NAMES = {
    "abs" : BuiltIn("abs"),
    "aiter" : BuiltIn("aiter"),
    "all" : BuiltIn("all"),
    "any" : BuiltIn("any"),
    "anext" : BuiltIn("anext"),
    "ascii" : BuiltIn("ascii"),
    "bin" : BuiltIn("bin"),
    "bool" : BuiltIn("bool"),
    "breakpoint" : BuiltIn("breakpoint"),
    "bytearray" : BuiltIn("bytearray"),
    "bytes" : BuiltIn("bytes"),
    "callable" : BuiltIn("callable"),
    "chr" : BuiltIn("chr"),
    "classmethod" : BuiltIn("classmethod"),
    "compile" : BuiltIn("compile"),
    "complex" : BuiltIn("complex"),
    #TODO: add more built-ins
    "print" : BuiltIn("print"),
}

class Parser:
    def __init__(self, names : dict[str, AbstractObject] = ..., stack : list[AbstractObject] = ..., active_jumps : list[Jump] = ..., calls : list[Call] = ..., kw_names : list[str] = ...):
        self.set_state(names=names, stack=stack, active_jumps=active_jumps, calls=calls, kw_names=kw_names)

    def set_state(self, names : dict[str, AbstractObject] = ..., stack : list[AbstractObject] = ..., active_jumps : list[Jump] = ..., calls : list[Call] = ..., kw_names : list[str] = ...):
        if names == ...:
            self.names : dict[str, AbstractObject] = BASE_NAMES
        else:
            self.names : dict[str, AbstractObject] = names
        
        if stack == ...:
            self.stack : list[AbstractObject] = []
        else:
            self.stack : list[AbstractObject] = stack
        
        if active_jumps == ...:
            self.active_jumps : list[Jump] = []
        else:
            self.active_jumps : list[Jump] = active_jumps
        
        if calls == ...:
            self.calls : list[Call] = []
        else:
            self.calls : list[Call] = calls
        
        if kw_names == ...:
            self.kw_names : list[str] = []
        else:
            self.kw_names : list[str] = kw_names

    def parse(self, bytecode : dis.Bytecode, reset_state = True):
        if reset_state:
            self.set_state()
        for line in bytecode:
            self.parse_line(line)

    def parse_line(self, line : dis.Instruction):
        match (line.opname, line.argval):
            case "RESUME", _:
                pass
            case "PUSH_NULL", _:
                self.stack.append(None)
                print("PUSH NULL")
            case "POP_TOP", _:
                self.stack.pop()
                print("POP TOP")

            case "IMPORT_NAME", mdl:
                self.stack.append(Module(mdl))
                print("IMPORT", mdl)

            case "LOAD_CONST", const:
                self.stack.append(Value(const))
                print("LOAD CONST", const)
            case "LOAD_NAME", name:
                self.stack.append(self.names.get(name, UnknownName(name)))
                print("LOAD NAME", name)
            case "LOAD_ATTR", attr:
                attr_of = stack.pop()
                self.stack.append(Attribute(attr_of, attr, attr_of.get_attr(attr)))
                print("LOAD ATTR of", attr_of, "name", attr)

            case "STORE_NAME", name:
                if not self.active_jumps:
                    print("STORE NAME (no active jumps)", name)
                    self.names[name] = self.stack.pop()
                elif name in self.names.keys():
                    if isinstance(self.names[name], PossibleOutcomes):
                        print(f"STORE NAME ({len(self.active_jumps)} active jumps)", name)
                        self.names[name].add_outcome(Outcome())
                    else:
                        print(f"STORE NAME ({len(self.active_jumps)} active jumps + changed to possibleOutcomes)", name)
                        before = self.names[name]
                        self.names[name] = PossibleOutcomes(
                            [Outcome([i["condition"] for i in self.active_jumps], self.stack.pop())],
                            else_outcome=before
                        )
            case "STORE_ATTR", attr:
                to = self.stack.pop()
                val = self.stack.pop()
                to.set_attr(attr, val)
                print("STORE ATTR of", val, "name", attr)

            case "COMPARE_OP", comp:
                obj2 = self.stack.pop()
                obj1 = self.stack.pop()
                self.stack.append(Compare(comp, obj1, obj2))
                print("COMPARE", obj1, comp, obj2)
            case "POP_JUMP_FORWARD_IF_FALSE", _:
                destination = line.argval
                condition = self.stack.pop()
                self.active_jumps.append({
                    "condition": condition,
                    "destination": destination
                })
                print("POP_JUMP_FORWARD_IF not", condition, "to", destination)

            case "PRECALL", attrcount:
                print("PRECALL", attrcount)
            case "KW_NAMES":
                self.kw_names = line.arg
            case "CALL", attrcount:
                attrs = []
                kwattrs = {}
                
                for i in range(attrcount):
                    if i < kw_names:
                        pass
                    attrs.insert(0, self.stack.pop())
                func = self.stack.pop()
                call = Call(func, attrs)
                self.calls.append(call)
                self.stack.append(call)
                print("CALL", attrcount)
                
            case _, _:
                print("FAILED", line)

print()
print("STACK:")
print(*stack, sep="\n")
print()
print("NAMES:")
print(*(f"{k} : {v}" for k, v in names.items()), sep="\n")
print()
print("CALLS:")
print(*calls, sep="\n")