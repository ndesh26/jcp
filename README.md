# Java Compiler in Python (JCP)

This project is a part of the course Compiler Design (CS 335), IIT Kanpur. This is a Java 
compiler implemented in python3 with x86 as the target language.

This compiler is a multi-parse compiler, i.e., it first generates an AST 
(Abstract Syntax Tree form) file and then, it generates a TAC
(Three Address Code) file which then is used for the generation of assembly
files.

### References

* The grammar that we have used is taken from [plyj](https://github.com/musiKk/plyj)

### Setup

```
sudo pip3 install -r requirements.txt
```

### Dependencies

* pydot
* ply

### Usage

```
python3 jcp/parser.py [-g] path_to_file/file_name
```

-g: debug flag

### Modules

* jcp/

    * lexer.py: contains the token definitions
    * parser_rules.py: contains grammar rules and their corresponding actions
    * parser.py: initlizes parser and reads the file writes the output
    * ptg.py(parse tree generator): contains helper functions to generate parse tree
    * 3addrcode.py: generates TAC (Three Address Code) and it's corresponding assembly, object files
    * symbol_table.py: handles symbol tables for a program by having a class table

* helper/

    * fileio.s: handles the file IO actions
    * mem.s: code for heap allocation
    * printing.s: code for stdio

### Contributors

* Nayan Deshmukh
* Rohith Mukku
