import os
import sys
import ply.yacc as yacc
from parser_rules import JavaParser
import ptg
code = __import__('3addrcode')

if len(sys.argv) < 2:
    print("Usage: {} [-g] filename".format(sys.argv[0]))
    exit()

if sys.argv[1] == "-g":
    debug = 1
else:
    debug = 0
# Build the parser
parser = yacc.yacc(module=JavaParser(), start='goal')
if len(sys.argv) == 3:
    if type(sys.argv[2]) == str:
        _file = open(sys.argv[2])
    content = _file.read()
else:
    if type(sys.argv[1]) == str:
        _file = open(sys.argv[1])
    content = _file.read()
if not os.path.exists("csv"):
    os.makedirs("csv")
result = parser.parse("++"+content, debug=debug)
tac = code.Tac()
tac.generate_tac(result)
# tac.print_tac()
tac.print_x86()
