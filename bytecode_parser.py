from dataclasses import dataclass, field, asdict
import dis
from enum import Enum
from types import CodeType
from typing import Any, Self

@dataclass
class AbstractObject:
    def __post_init__(self):
        self.modified_attrs = dict()

    def set_attr(self, attr, val):
        self.modified_attrs[attr] = val
    def get_attr(self, attr):
        return self.modified_attrs.get(attr, Unknown())
    def remove_modified_attr(self, attr):
        del self.modified_attrs[attr]

@dataclass
class Unknown(AbstractObject):
    pass

@dataclass
class UnknownName(AbstractObject):
    name : str = None

@dataclass
class UnknownFastName(AbstractObject):
    name : str = None

@dataclass
class Value(AbstractObject):
    value : Any = None

@dataclass
class Attribute(AbstractObject):
    attr_of : AbstractObject = None
    name : str = None
    value : AbstractObject = None

@dataclass
class Module(AbstractObject):
    name : str = None

@dataclass
class BuiltIn(AbstractObject):
    name : str = None

@dataclass
class Call(AbstractObject):
    func : AbstractObject = None
    args : list[AbstractObject] = None
    kwargs : dict[str, AbstractObject] = field(default_factory=lambda: {})

@dataclass
class Operation(AbstractObject):
    op : str = None
    obj1 : AbstractObject = None
    obj2 : AbstractObject = None

@dataclass
class UnaryOperation(AbstractObject):
    op : str = None
    obj : AbstractObject = None

@dataclass
class Compare(AbstractObject):
    comp : str = None
    obj1 : AbstractObject = None
    obj2 : AbstractObject = None

@dataclass
class Outcome:
    conditions : list[AbstractObject] = field(default_factory=lambda: [])
    outcome : AbstractObject = None

@dataclass
class PossibleOutcomes(AbstractObject):
    outcomes : list[Outcome] = field(default_factory=lambda: [])
    else_outcome : AbstractObject = None

    def add_outcome(self, outcome : Outcome):
        self.outcomes.insert(0, outcome)

@dataclass
class Jump:
    condition : AbstractObject = None
    destination : int = None

@dataclass
class OrStack:
    condition : AbstractObject = None
    end : int = None

@dataclass
class LoopDetection:
    start : int = None
    end : int = None

class LoopModificationType(Enum):
    VALUE = 0
    BREAK = 1
    CONTINUE = 2

@dataclass
class LoopModification:
    type : LoopModificationType = LoopModificationType.VALUE
    value : AbstractObject | str = None
    result : AbstractObject = None

class WhileLoop(AbstractObject):
    def __init__(self, base_values : dict[str, AbstractObject], base_values_fast : dict[str, AbstractObject], modifications : list[LoopModification], condition : AbstractObject):
        self.base_values = base_values
        self.base_values_fast = base_values_fast
        self.modifications = modifications
        self.condition = condition

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

@dataclass
class ParserState:
    consts : list = field(default_factory=list)
    
    names : dict[str, AbstractObject] = field(default_factory = lambda: BASE_NAMES.copy())
    
    fast_names : dict[str, AbstractObject] = field(default_factory=dict)
    
    stack : list[AbstractObject] = field(default_factory=list)
    
    active_jumps : list[Jump] = field(default_factory=list)
    
    or_stack : list[OrStack] = field(default_factory=list)
    
    calls : list[Call] = field(default_factory=list)
    
    kw_names : list[str] = field(default_factory=list)
    
    return_value : AbstractObject | None = None
    
    loops_detected : list[LoopDetection] = field(default_factory=list)

class Parser:
    def __init__(self, state=...):
        self.set_state(state)
    
    @classmethod
    def from_state(cls, state : ParserState):
        self = cls()
        self.set_state(state=state)
        return self
    
    def get_state(self):
        return ParserState()
    
    def set_state(self, state : ParserState = ...):
        if (state == ...):
            state = ParserState()
            
        for k, v in asdict(state).items():
            setattr(self, k, v)

    def parse(self, bytecode : dis.Bytecode | CodeType, reset_state = True):
        if isinstance(bytecode, CodeType):
            bytecode = dis.Bytecode(bytecode)
        if reset_state:
            self.set_state()
        self.prepare(bytecode)
        for line in bytecode:
            self.decay_jumps(line.offset)

            if not self.parse_line(line):
                break
    
    def prepare(self, bytecode):
        loop_started = 0
        loop_jump = None
        loop_start = None
        loop_end = None
        loop_ended = False
        for line in bytecode:
            line : dis.Instruction
            if loop_ended:
                if line.is_jump_target:
                    print(loop_start, loop_end)
                loop_ended = False
                continue
            if loop_started == 0:
                if line.opname == "POP_JUMP_FORWARD_IF_FALSE":
                    loop_started = 1
                    loop_start = line.offset
            elif loop_started == 1:
                if line.is_jump_target:
                    loop_started = 2
                    loop_jump = line.offset
                else:
                    loop_started = 0
            elif loop_started == 2:
                if line.opname == "POP_JUMP_BACKWARD_IF_TRUE":
                    if line.argval == loop_jump:
                        loop_end = line.offset
                        loop_ended = True
                
    
    def decay_jumps(self, pos):
        active_jumps_to_remove = []
        for active_jump in self.active_jumps:
            if pos > active_jump.destination and active_jump.destination != -1:
                active_jumps_to_remove.append(active_jump)
        for active_jump in active_jumps_to_remove:
            self.active_jumps.remove(active_jump)

        or_stack_items_to_remove = []
        for or_stack in self.or_stack:
            if pos > or_stack.end:
                or_stack_items_to_remove.append(or_stack)
        for or_stack in or_stack_items_to_remove:
            self.or_stack.remove(or_stack)

    def parse_line(self, line : dis.Instruction):
        f = None
        match line.opname:
            case "RESUME":
                f = self.parse_RESUME
            case "PUSH_NULL":
                f = self.parse_PUSH_NULL
            case "POP_TOP":
                f = self.parse_POP_TOP
            case "IMPORT_NAME":
                f = self.parse_IMPORT_NAME
            case "LOAD_CONST":
                f = self.parse_LOAD_CONST
            case "LOAD_NAME":
                f = self.parse_LOAD_NAME
            case "LOAD_FAST":
                f = self.parse_LOAD_FAST
            case "LOAD_ATTR":
                f = self.parse_LOAD_ATTR
            case "STORE_NAME":
                f = self.parse_STORE_NAME
            case "STORE_FAST":
                f = self.parse_STORE_FAST
            case "STORE_ATTR":
                f = self.parse_STORE_ATTR
            case "COMPARE_OP":
                f = self.parse_COMPARE_OP
            case "POP_JUMP_FORWARD_IF_FALSE":
                f = self.parse_POP_JUMP_FORWARD_IF_FALSE
            case "POP_JUMP_FORWARD_IF_TRUE":
                f = self.parse_POP_JUMP_FORWARD_IF_TRUE
            case "PRECALL":
                f = self.parse_PRECALL
            case "KW_NAMES":
                f = self.parse_KW_NAMES
            case "CALL":
                f = self.parse_CALL
            case "RETURN_VALUE":
                f = self.parse_RETURN
            case "BINARY_OP":
                f = self.parse_BINARY_OP
            case _:
                f = self.parse_UNKNOWN

        res = f(line.argval, line)
        return False if res == False else True

    def parse_RESUME(self, argval, line):
        print("RESUME")
    
    def parse_PUSH_NULL(self, argval, line):
        self.stack.append(None)
        print("PUSHNULL")
        
    def parse_POP_TOP(self, argval, line):
        self.stack.pop()
        print("POP TOP")
        
    def parse_IMPORT_NAME(self, argval, line):
        self.stack.append(Module(argval))
        print("IMPORT NAME")
    
    def parse_LOAD_CONST(self, argval, line):
        self.stack.append(Value(argval))
        print(f"LOAD CONST {argval}")
        
    def parse_LOAD_NAME(self, argval, line):
        self.stack.append(self.names.get(argval, UnknownName(argval)))
        print(f"LOAD NAME {argval}")
        
    def parse_LOAD_FAST(self, argval, line):
        self.stack.append(self.fast_names.get(argval, UnknownFastName(argval)))
        print(f"LOAD NAME {argval}")
    
    def parse_LOAD_ATTR(self, argval, line):
        attr_of = self.stack.pop()
        self.stack.append(Attribute(attr_of, argval, attr_of.get_attr(argval)))
        print(f"LOAD ATTR {argval} of {attr_of}")
    
    def parse_STORE_NAME(self, argval, line):
        if not self.active_jumps:
            print(f"STORE NAME (no active jumps) {argval}")
            self.names[argval] = self.stack.pop()
        elif isinstance(self.names.get(argval, None), PossibleOutcomes):
            print(f"STORE NAME ({len(self.active_jumps)} active jumps) {argval}")
            self.names[argval].add_outcome(Outcome([i.condition for i in self.active_jumps], self.stack.pop()))
        else:
            print(f"STORE NAME ({len(self.active_jumps)} active jumps + changed to possibleOutcomes) {argval}")
            before = self.names.get(argval, None)
            self.names[argval] = PossibleOutcomes(
                [Outcome([i.condition for i in self.active_jumps], self.stack.pop())],
                else_outcome=before
            )
    
    def parse_STORE_FAST(self, argval, line):
        if not self.active_jumps:
            print(f"STORE FAST (no active jumps) {argval}")
            self.fast_names[argval] = self.stack.pop()
        elif isinstance(self.names.get(argval, None), PossibleOutcomes):
            print(f"STORE FAST ({len(self.active_jumps)} active jumps) {argval}")
            self.fast_names[argval].add_outcome(Outcome([i.condition for i in self.active_jumps], self.stack.pop()))
        else:
            print(f"STORE FAST ({len(self.active_jumps)} active jumps + changed to possibleOutcomes) {argval}")
            before = self.fast_names.get(argval, None)
            self.fast_names[argval] = PossibleOutcomes(
                [Outcome([i.condition for i in self.active_jumps], self.stack.pop())],
                else_outcome=before
            )
    
    def parse_STORE_ATTR(self, argval, line):
        to = self.stack.pop()
        val = self.stack.pop()
        to.set_attr(argval, val)
        print(f"STORE ATTR {argval} of {val}")
    
    def parse_COMPARE_OP(self, argval, line):
        obj2 = self.stack.pop()
        obj1 = self.stack.pop()
        self.stack.append(Compare(argval, obj1, obj2))
        print(f"COMPARE {obj1} {argval} {obj2}")
    
    def parse_POP_JUMP_FORWARD_IF_FALSE(self, argval, line):
        destination = argval
        condition = self.stack.pop()
        for or_stack in self.or_stack:
            condition = Operation(op="or", obj1=condition, obj2=or_stack.condition)
        self.or_stack = []
        self.active_jumps.append(Jump(condition=condition, destination=destination))
        print(f"POP JUMP FORWARD IF NOT {condition} to {destination}")
    
    def parse_POP_JUMP_FORWARD_IF_TRUE(self, argval, line):
        end = argval
        self.or_stack.append(OrStack(condition=self.stack.pop(), end=end))
        print(f"POP_JUMP_FORWARD_IF to {end}")
    
    def parse_PRECALL(self, argval, line):
        print("PRECALL {argval}")
    
    def parse_KW_NAMES(self, argval, line):
        self.kw_names = line.arg
        print(f"KW NAMES {line.arg}")
    
    def parse_CALL(self, argval, line):
        attrs = []
        kwattrs = {}
        
        for i in range(argval):
            if i in self.kw_names:
                kwattrs[i] = self.stack.pop()
            else:
                attrs.insert(0, self.stack.pop())
        
        self.kw_names = []
        func = self.stack.pop()
        call = Call(func, attrs, kwattrs)
        
        call_outcomes = PossibleOutcomes(
            [Outcome([i.condition for i in self.active_jumps], call)]
        )
        
        self.calls.append(call_outcomes)
        self.stack.append(call_outcomes)
        print(f"CALL {argval}")
    
    def parse_RETURN(self, argval, line):
        if not self.active_jumps:
            self.return_value = self.stack.pop()
            print("RETURN WITH NO CONDITION")
            print("Halt.")
            return False
        else:
            if self.return_value == None:
                self.return_value = PossibleOutcomes([
                    Outcome([i.condition for i in self.active_jumps], self.stack.pop())
                ])
            elif isinstance(self.return_value, PossibleOutcomes):
                self.return_value.add_outcome(
                    Outcome([i.condition for i in self.active_jumps], self.stack.pop())
                )
            else:
                raise ValueError("Weird return value.")
        
            # adding condition of executing code after return
            for active_jump in self.active_jumps.copy():
                self.active_jumps.append(Jump(UnaryOperation("not", active_jump.condition), -1))

        print("RETURN VALUE")
    
    def parse_BINARY_OP(self, argval, line):
        arg2 = self.stack.pop()
        arg1 = self.stack.pop()
        self.stack.append(Operation(line.argrepr, arg1, arg2))
        print(f"BINARY {line.argrepr}")
    
    def parse_UNKNOWN(self, argval, line):
        print(f"UNKNOWN {line.opname} {line}")

def main():
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

    source_basic_loop = '''
a = 0
while b > 0:
    a = a + 1
    b = b - 1
print(a)
    '''

    #comp = compile(source_basic_if, "test", "exec")

    def func():
        a = 5
        while a > 0:
            while a < 0:
                a -= 1
            
        a
        a
        a
        a
        a
        
    
    comp = func.__code__

    bytecode = dis.Bytecode(comp)
    constants = bytecode.codeobj.co_consts
    print(bytecode.dis())
    
    parser = Parser(consts=constants)
    parser.parse(bytecode)
    
    print()
    print("STACK:")
    print(*parser.stack, sep="\n")
    print()
    print("NAMES:")
    print(*(f"{k} : {v}" for k, v in parser.names.items()), sep="\n")
    print()
    print("CALLS:")
    print(*parser.calls, sep="\n")
    print()
    print("RETURN:")
    print(parser.return_value)

if __name__ == "__main__":
    main()