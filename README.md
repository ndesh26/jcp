# Java Compiler in Python (JCP)

This project is part of a Introduction to Compilers Course. We have used python3 as
the implementation language, java as the source language and x86 as the target language.

### Setup

```
sudo pip3 install -r requirements.txt
```

### Running

```
python3 jcp/parser.py [-g] file_name
```

-g: debug flag

### Dependencies

* pydot
* ply

### Modules

* lexer: contains the token definitions
* parser_rules: contains grammar rules and their corresponding actions
* parser: initlizes parser and reads the file writes the output
* ptg(parse tree generator): contains helper functions to generate parse tree

### References

* The grammar that we have used is taken from [plyj](https://github.com/musiKk/plyj)
