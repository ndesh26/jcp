import sys
import ply.yacc as yacc
from parser_rules import JavaParser
import ast

if len(sys.argv) != 3:
    print("Usage: {} parser filename".format(sys.argv[0]))
    exit()
    
# Build the parser
parser = yacc.yacc(module=JavaParser(), start='goal')
if type(sys.argv[2]) == str:
    _file = open(sys.argv[2])
content = _file.read()

if sys.argv[1] == 'expression':
    prefix = '--'
elif sys.argv[1] == 'program':
    prefix = '++'
elif sys.argv[1] == 'statement':
    prefix = '**'
else:
    print("Parser not found")
    exit()
   
result = parser.parse(prefix+content, debug=1)
ast.end()
