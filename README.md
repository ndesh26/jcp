# Java Compiler in Python (JCP)

This project is part of a Introduction to Compilers Course. We have used python3 as
the implementation language, java as the source language and x86 as the target language.

### Setup

```
sudo pip3 install -r requirements.txt
```
### Dependencies

* pydot
* ply

### Modules

* lexer: contains the token definitions
* parser_rules: contains grammar rules and their corresponding actions
* parser: initlizes parser and reads the file writes the output
* ptg(parse tree generator): contains helper functions to generate parse tree

### References

* The grammar that we have used is inspired by [ANTLR Java Grammar](https://github.com/antlr/antlr4/blob/master/tool-testsuite/test/org/antlr/v4/test/tool/Java.g4)
* The class structure and lexer is inspired by [plyj](https://github.com/musiKk/plyj)
