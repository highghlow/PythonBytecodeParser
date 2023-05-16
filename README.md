# Python Bytecode Parser
This project could predict the output variables of a python program from its bytecode
## This project does not support most of python bytecode operations
Please submit pull requests to speed up development

## Quickstart
```python
import bytecode_parser
example_code = '''
input_value = val # Will be replaced with UnknownName(name="val") by the parser
a = 0
if input_value > 0:
    a = 1
'''
compiled = compile(example_code, "__name__value_here__", "exec")
parser = bytecode_parser.Parser()
parser.parse(compiled)
print(parser.names["a"])
# PossibleOutcomes(outcomes=[
#     Outcome(conditions=[ // condition1 AND condition2 AND ...
#         Compare(
#             comp='>',
#             obj1=UnknownName(name='val'),
#             obj2=Value(value=0))],
#     outcome=Value(value=1))],
# else_outcome=Value(value=0))
```

## Explanation

Python code
```python
a = int(input())
if a > 0:
    print("Positive")
else:
    print("Negative")
```
Compiles to this bytecode
```
<...input call code here...>
54 STORE_FAST a                     // STACK: []
56 LOAD_FAST a                      // STACK: [< value a >]
58 LOAD_CONST 0                     // STACK: [< value a >, 0]
60 COMPARE_OP >                     // STACK: [< value a>0 >]
66 POP_JUMP_FORWARD_IF_FALSE to 102 // STACK: [< value a>0 >]
// IF a > 0
68 LOAD_GLOBAL 5 print              // STACK: [print]
80 LOAD_CONST 'Positive'            // STACK: [print, 'Positive']
82 PRECALL 1                        // STACK: [print, 'Positive']
86 CALL 1                           // STACK: [print] / CALLED print('Positive')
96 POP_TOP                          // STACK: []
98 LOAD_CONST None                  // STACK: [None]
100 RETURN_VALUE                    // RETUNED None
# ELSE
>> 102 LOAD_GLOBAL print            // STACK: [print]
114 LOAD_CONST 'Negative'           // STACK: [print, 'Negative']
116 PRECALL 1                       // STACK: [print, 'Negative']
120 CALL 1                          // STACK: [print]
130 POP_TOP                         // STACK: []
132 LOAD_CONST None                 // STACK: [None]
134 RETURN_VALUE                    // RETURNED None
```
So the parser would result in:
```
CALLS: [
    print("Positive") if int(input()) > 0
    print("Negative") if not (int(input()) > 0)
]
```