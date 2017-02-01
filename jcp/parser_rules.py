import ply.yacc as yacc
import ast

from lexer import tokens

def p_expression(p):
    '''expression : additive_expression'''
    ast.end()
    p[0] = p[1]

def p_par_expression(p):
    '''par_expression : LPAREN expression RPAREN'''
    p[0] = p[1] + p[2] + p[3]


def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_multiplicative_expression(p):
    '''multiplicative_expression : unary_expression
                                 | multiplicative_expression TIMES unary_expression
                                 | multiplicative_expression BY unary_expression'''

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_unary_expression(p):
    '''unary_expression : PLUS unary_expression
                        | MINUS unary_expression
                        | primary'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]

def p_primary(p):
    '''primary : literal
               | IDENTIFIER
               | par_expression'''
    p[0] = p[1]

def p_literal(p):
    '''literal : NUMBER'''
    p[0] = ast.single_node(p[1])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

while True:
   try:
       s = input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
