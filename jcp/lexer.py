#-----------------------------------------------------------------------------------
# lexer.py
# Lexer for Java programming language in Python
# Reference: https://docs.oracle.com/javase/specs/jls/se7/html/jls-18.html
#-----------------------------------------------------------------------------------

import ply.lex as lex

# Reference: https://docs.oracle.com/javase/tutorial/java/nutsandbolts/_keywords.html
keywords = ('abstract', 'assert', 'boolean', 'break', 'byte',
            'case', 'catch', 'char', 'class', 'const', 'continue',
            'default', 'do', 'double', 'else', 'enum', 'extends',
            'final', 'finally', 'float', 'for', 'goto', 'if',
            'implements', 'import', 'instanceof', 'int', 'interface',
            'long', 'native', 'new', 'package', 'private', 'protected',
            'public', 'return', 'short', 'static', 'strictfp', 'super',
            'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'try', 'void', 'volatile', 'while')

# Reference: https://docs.oracle.com/javase/tutorial/java/nutsandbolts/operators.html
# Tokens definitions
tokens = [
        'IDENTIFIER',
        'NUMBER',
        'CHARACTER',
        'STRING',
        'LINE_COMMENT', 'BLOCK_COMMENT',

        'OR', 'AND', 'BIT_OR', 'BIT_AND',
        'EQ', 'NE', 'GE', 'LE',

        'PLUS', 'MINUS', 'LPAREN', 'RPAREN',
        'TIMES', 'BY', 'GT', 'LT', 'REMAINDER',
        'RBRACE', 'LBRACE','LSQRBRACKET', 'RSQRBRACKET',

        'LSHIFT', 'RSHIFT', 'RRSHIFT',

        'INCR', 'DECR',

        'EQUALITY', 'NEQUALITY',

        'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN','BY_ASSIGN',
        'REMAINDER_ASSIGN', 'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN', 'RRSHIFT_ASSIGN',
        'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN',

        'TERNARY', 'XOR', 'SEMICOLON', 'COMMA', 'DOT',
        'QUESTION', 'COLON'
        ] + [k.upper() for k in keywords]

t_NUMBER        = r'\d+'
t_CHARACTER     = r'\'([^\\\n]|(\\.))*?\''
t_STRING        = r'\"([^\\\n]|(\\.))*?\"'
t_LINE_COMMENT  = '//.*'

def t_BLOCK_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

# LOGICAL and BITWISE OPERATIONS
t_OR        = r'\|\|'
t_AND       = r'&&'
t_BIT_OR    = r'\|'
t_BIT_AND   = r'&'
t_XOR       = r'\^'

# COMPARISIONS
t_GT    = '>'
t_LT    = '<'
t_EQ    = '='
t_NE    = '!='
t_GE    = '>='
t_LE    = '<='

# ARITHEMETIC OPERATIONS
t_PLUS      = r'\+'
t_MINUS     = r'\-'
t_TIMES     = r'\*'
t_BY        = r'/'
t_REMAINDER = '%'

# SHIFT
t_LSHIFT    = '<<'
t_RSHIFT    = '>>'
t_RRSHIFT   = '>>>'

# INCREMENT & DECREMENT
t_INCR      = r'\+\+'
t_DECR      = r'\-\-'

# EQUALITY
t_EQUALITY  = '=='

# ASSIGNMENT
t_PLUS_ASSIGN       = r'\+='
t_MINUS_ASSIGN      = '-='
t_TIMES_ASSIGN      = r'\*='
t_BY_ASSIGN         = '/='
t_REMAINDER_ASSIGN  = '%='
t_LSHIFT_ASSIGN     = '<<='
t_RSHIFT_ASSIGN     = '>>='
t_RRSHIFT_ASSIGN    = '>>>='
t_AND_ASSIGN        = '&='
t_OR_ASSIGN         = r'\|='
t_XOR_ASSIGN        = '\^='

# BRACKETS
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_LSQRBRACKET= r'\['
t_RSQRBRACKET= r'\]'

# DELIMITER
t_SEMICOLON = r';'
t_COMMA     = r','
t_DOT       = r'\.'
t_QUESTION  = r'\?';
t_COLON     = r':';

# Ignore indentation
t_ignore    = ' \t'

# VARIABLES & NEWLINES
def t_IDENTIFIER(t):
    '[A-Za-z_$][A-Za-z0-9_$]*'
    if t.value in keywords:
        t.type = t.value.upper()
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_newline2(t):
    r'\r\n'
    t.lexer.lineno += len(t.value)/2

def t_error(t):
    print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
    t.lexer.skip(1)

# Lexer build
lexer = lex.lex()
