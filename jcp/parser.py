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

# Read the file
if type(sys.argv[len(sys.argv)-1]) == str:
    _file = open(sys.argv[len(sys.argv)-1])
    outfile = sys.argv[len(sys.argv)-1].split(".")[0]
content = _file.read()

# activate the parser
result = parser.parse("++"+content, debug=debug)
if result==None or result.type == "error":
    print("Program Terminated")
else:
    if not os.path.exists("bin"):
        os.makedirs("bin")
    if not os.path.exists("assembly"):
        os.makedirs("assembly")
    if not os.path.exists("tac"):
        os.makedirs("tac")
    # Generate TAC
    tac = code.Tac()
    tac.generate_tac(result)
    file_name = outfile[outfile.rfind('/'):]
    sys.stdout = open("tac/"+file_name+".tac", 'w')
    tac.print_tac()
    sys.stdout.close()
    # Generate X86
    sys.stdout = open("assembly/"+file_name+".s", 'w')
    print("global main\nextern printInt\nextern printlnInt\nextern scanInt\nextern printChar\nextern printString\n")
    print("extern open\nextern close\nextern create\nextern readChar\nextern writeChar\nextern mem\nsection .text\n")
    tac.print_x86()
    sys.stdout.close()
    # compile and link the binary
    call('nasm -f elf32 assembly/' + file_name + '.s', shell=True)
    call('nasm -f elf32 helper/printing.s', shell=True)
    call('nasm -f elf32 helper/fileio.s', shell=True)
    call('nasm -f elf32 helper/mem.s', shell=True)
    call('cc -m32 assembly/' + file_name + '.o helper/printing.o helper/fileio.o helper/mem.o -o bin/' + file_name, shell=True)
