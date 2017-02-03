import ply.yacc as yacc
import ast

from lexer import tokens

def p_expression(p):
    '''expression : logical_expression
                  | logical_expression assignment_operator expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("expression", p[1])
    else:
        p[0] =  ast.binary_op(p[2], p[1], p[3])
    ast.end()

def p_constant_expression(p):
    '''constant_expression : expression'''
    p[0] = ast.unary_op("constant_expression", tmp)


def p_assignment_operator(p):
    '''assignment_operator : EQ
                           | PLUS_ASSIGN
                           | MINUS_ASSIGN
                           | TIMES_ASSIGN
                           | BY_ASSIGN
                           | REMAINDER_ASSIGN
                           | LSHIFT_ASSIGN
                           | RSHIFT_ASSIGN
                           | RRSHIFT_ASSIGN
                           | AND_ASSIGN
                           | OR_ASSIGN
                           | XOR_ASSIGN'''
    p[0] = p[1]

def p_par_expression(p):
    '''par_expression : LPAREN expression RPAREN'''
    p[0] = p[2]

# Ternary expression grammar not implemented

def p_logical_expression(p):
    '''logical_expression : bitwise_expression
                          | logical_expression AND bitwise_expression
                          | logical_expression OR bitwise_expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("bitwise_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_bitwise_expression(p):
    '''bitwise_expression : equality_expression
                          | bitwise_expression BIT_AND equality_expression
                          | bitwise_expression BIT_OR equality_expression
                          | bitwise_expression XOR equality_expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("bitwise_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])


def p_equality_expression(p):
    '''equality_expression : comparision_expression
                           | equality_expression EQUALITY comparision_expression
                           | equality_expression NE comparision_expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("equality_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])


def p_comparision_expression(p):
    '''comparision_expression : shift_expression
                              | comparision_expression LE shift_expression
                              | comparision_expression GE shift_expression
                              | comparision_expression LT shift_expression
                              | comparision_expression GT shift_expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("comparison_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_shift_expression(p):
    '''shift_expression : additive_expression
                        | shift_expression LSHIFT additive_expression
                        | shift_expression RSHIFT additive_expression
                        | shift_expression RRSHIFT additive_expression'''
    if len(p) == 2:
        p[0] = ast.unary_op("shift_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''

    if len(p) == 2:
        p[0] = ast.unary_op("additive_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_multiplicative_expression(p):
    '''multiplicative_expression : unary_expression
                                 | multiplicative_expression TIMES unary_expression
                                 | multiplicative_expression BY unary_expression'''

    if len(p) == 2:
        p[0] = ast.unary_op("multiplicative_expression", p[1])
    else:
        p[0] = ast.binary_op(p[2], p[1], p[3])

def p_unary_expression(p):
    '''unary_expression : PLUS unary_expression
                        | MINUS unary_expression
                        | primary'''
    if len(p) == 2:
        p[0] = ast.unary_op("unary_expression", p[1])
    else:
        tmp = ast.unary_op(p[1], p[2])
        p[0] = ast.unary_op("unary_expression", tmp)

def p_primary(p):
    '''primary : literal
               | par_expression'''
    p[0] = ast.unary_op("primary", p[1])

def p_primary_identifier(p):
    '''primary : IDENTIFIER'''
    tmp = ast.single_node(p[1])
    p[0] = ast.unary_op("primary", tmp)

def p_literal(p):
    '''literal : NUMBER'''
    tmp = ast.single_node(p[1])
    p[0] = ast.unary_op("literal", tmp)

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
