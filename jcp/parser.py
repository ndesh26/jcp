import os
import sys
import ply.yacc as yacc
from subprocess import call
from parser_rules import JavaParser
from parser_rules import ast
import ptg
code = __import__('3addrcode')

if len(sys.argv) < 2:
    print("Usage: {} [-g] filename".format(sys.argv[0]))
    exit()

if "-g" in sys.argv:
    debug = 1
else:
    debug = 0
# Build the parser
parser = yacc.yacc(module=JavaParser(), start='goal')
# if len(sys.argv) == 3:
    # if type(sys.argv[2]) == str:
        # _file = open(sys.argv[2])
        # outfile = sys.argv[2].split(".")[0]
    # content = _file.read()
# else:
if type(sys.argv[len(sys.argv)-1]) == str:
    _file = open(sys.argv[len(sys.argv)-1])
    outfile = sys.argv[len(sys.argv)-1].split(".")[0]
content = _file.read()
if not os.path.exists("csv"):
    os.makedirs("csv")
result = parser.parse("++"+content, debug=debug)
if result.type == "error":
    print("Program Terminated")
else:
    tac = code.Tac()
    tac.generate_tac(result)
    sys.stdout = open(outfile+".tac", 'w')
    tac.print_tac()
    sys.stdout.close()
    sys.stdout = open(outfile+".s", 'w')
    print("global main\nextern printInt\nextern printlnInt\nextern scanInt\nextern printChar\n")
    print("extern open\nextern close\nextern create\nextern readChar\nextern writeChar\nsection .text\n")
    tac.print_x86()
    sys.stdout.close()
    call('nasm -f elf32 ' + outfile + '.s', shell=True)
    call('nasm -f elf32 helper/printing.s', shell=True)
    call('nasm -f elf32 helper/fileio.s', shell=True)
    call('cc -m32 ' + outfile + '.o helper/printing.o helper/fileio.o -o ' + outfile, shell=True)
