from bytecode_parser import AbstractObject, Parser, ParserState
import bytecode_parser

class Solver:
    def __init__(self, initial_state=None, initial_parser_state=...):
        if initial_parser_state != ...:
            self.parser_state = initial_parser_state
        else:
            self.parser_state = ParserState()
        self.state = initial_state

    def solve_state(self, state : ParserState):
        pass

    def solve(self, object : AbstractObject, state=...):
        if state == ...:
            state = self.state
        if isinstance(object, bytecode_parser.Attribute):
            f = self.solve_Attribute
        elif isinstance(object, bytecode_parser.BuiltIn):
            f = self.solve_BuiltIn
        elif isinstance(object, bytecode_parser.Call):
            f = self.solve_Call
        elif isinstance(object, bytecode_parser.Compare):
            f = self.solve_Compare
        elif isinstance(object, bytecode_parser.Module):
            f = self.solve_Module
        elif isinstance(object, bytecode_parser.Operation):
            f = self.solve_Operation
        elif isinstance(object, bytecode_parser.PossibleOutcomes):
            f = self.solve_PossibleOutcomes
        elif isinstance(object, bytecode_parser.UnaryOperation):
            f = self.solve_UnaryOperation
        elif isinstance(object, bytecode_parser.Unknown):
            f = self.solve_Unknown
        elif isinstance(object, bytecode_parser.UnknownName):
            f = self.solve_UnknownName
        elif isinstance(object, bytecode_parser.UnknownFastName):
            f = self.solve_UnknownFastName
        elif isinstance(object, bytecode_parser.Value):
            f = self.solve_Value
        f(object, self.state, self.parser_state)
    def solve_Attribute(obj : bytecode_parser.Attribute, state, parser_state : ParserState):
        pass
    def solve_BuiltIn(obj : bytecode_parser.BuiltIn, state, parser_state : ParserState):
        pass
    def solve_Call(obj : bytecode_parser.Call, state, parser_state : ParserState):
        pass
    def solve_Compare(obj : bytecode_parser.Compare, state, parser_state : ParserState):
        pass
    def solve_Module(obj : bytecode_parser.Module, state, parser_state : ParserState):
        pass
    def solve_Operation(obj : bytecode_parser.Operation, state, parser_state : ParserState):
        pass
    def solve_Unknown(obj : bytecode_parser.Unknown, state, parser_state : ParserState):
        pass
    def solve_UnknownName(obj : bytecode_parser.UnknownName, state, parser_state : ParserState):
        pass
    def solve_UnknownFastName(obj : bytecode_parser.UnknownFastName, state, parser_state : ParserState):
        pass
    def solve_PossibleOutcomes(obj : bytecode_parser.PossibleOutcomes, state, parser_state : ParserState):
        pass
    def solve_UnaryOperation(obj : bytecode_parser.UnaryOperation, state, parser_state : ParserState):
        pass