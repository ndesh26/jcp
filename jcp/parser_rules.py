import ply.yacc as yacc
import ast

from lexer import tokens

# Methods
def p_method_type_declaration(p):
    '''method_type_declaration : type method_declaration'''
    p[0] = ast.two_child_node(p[1], p[2])

def p_method_declaration(p):
    '''method_declaration : IDENTIFIER method_declarator_rest'''
    tmp = ast.node_create(p[1])
    p[0] = ast.two_child_node("method_declaration", tmp, p[2])

def p_method_declarator_rest(p):
    '''method_declarator_rest : formal_parameters
        ('throws' qualified_name_list)?
        (   method_body
        |   ';'
        )'''
    if len(p) == 3:
        tmp = ast.node_create(p[2])
        p[0] = ast.two_child_node("method_declarator_rest", p[1], tmp)
    # TODO: Implement graph for Exceptions

def p_formal_pararmeters(p):
    '''formal_parameters : LPAREN formal_parameter_decls RPAREN
                         | LPAREN RPAREN'''
    lparen = ast.node_create(p[1])
    if len(p) == 4:
        rparen = ast.node_create(p[3])
        p[0] = ast.three_child_node("formal_parameters", lparen, p[2], rparen)
    else:
        rparen = ast.node_create(p[2])
        p[0] = ast.two_child_node("formal_parameters", lparen, rparen)

def p_formal_parameter_decls(p):
    '''formal_parameter_decls : variable_modifiers type formal_parameter_decls_rest'''
    p[0] = ast.three_child_node("formal_parameter_decls", p[1], p[2], p[3])

def p_formal_parameter_decls_rest(p):
    '''formal_parameter_decls_rest : variable_declarator_id 
                                   | variable_declarator_id COMMA formal_parameter_decls
                                   | DOT DOT DOT variable_declarator_id'''
    if len(p) == 2:
        p[0] = ast.one_child_node("formal_parameter_decls_rest", p[0])
    else if len(p) == 4:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child.node("formal_parameter_decls_rest", p[1], tmp, p[3])
    # TODO: ... variabledeclaratorid

def p_method_body(p):
    '''method_body : block'''
    p[0] = ast.one_child_node("method_body", p[1])

def p_constructor_body(p):
    '''constructor_body : block'''
    p[0] = ast.one_child_node("constructor_body", p[1])

# Statements
def p_block(p):
    '''block : LBRACE block_statements RBRACE'''
    lbrace = ast.node_create(p[1])
    rbrace = ast.node_create(p[3])
    p[0] = ast.three_child_node("block", lbrace, p[2], rbrace)
    ast.end()

def p_block_statements(p):
    '''block_statements : block_statement
                        | block_statements block_statement'''
    if len(p) == 2:
        p[0] = ast.one_child_node("block_statements", p[1])
    else:
        p[0] = ast.two_child_node("block_statements", p[1], p[2])

def p_block_statement(p):
    '''block_statement : local_variable_declaration_statement
                       | statement'''
    p[0] = ast.one_child_node("block_statement", p[1])

def p_local_variable_declaration_statement(p):
    '''local_variable_declaration_statement : local_variable_declaration SEMICOLON'''
    tmp = ast.node_create(p[2])
    p[0] = ast.two_child_node("local_variable_declaration_statement", p[1], tmp)

def p_local_variable_declaration(p):
    '''local_variable_declaration : type variable_declarators
                                  | variable_modifiers type variable_declarators'''
    if len(p) == 3:
        p[0] = ast.two_child_node("local_variable_declaration", p[1], p[2])
    else:
        p[0] = ast.three_child_node("local_variable_declaration", p[1], p[2], p[3])

def p_variable_modfiers(p):
    '''variable_modifiers : variable_modifier
                          | variable_modifiers variable_modifier'''
    if len(p) == 2:
        p[0] = ast.one_child_node("variable_modifiers", p[1])
    else:
        p[0] = ast.two_child_node("variable_modifiers", p[1], p[2])

def p_variable_modifier(p):
    '''variable_modifier : FINAL'''
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("variable_modifier", tmp)

def p_statement_rule1(p):
    '''statement : block
                 | expression SEMICOLON'''
    if len(p) == 2:
        p[0] = ast.one_child_node("statement", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.two_child_node("statement", p[1], tmp)

def p_statement_rule2(p):
    '''statement : RETURN
                 | RETURN expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("statement", p[1])
    else:
        tmp = ast.node_create(p[1])
        p[0] = ast.three_child_node("statement", tmp, p[2])

def p_variable_declarators(p):
    '''variable_declarators : variable_declarator
                            | variable_declarators COMMA variable_declarator'''
    if len(p) == 2:
        p[0] = ast.one_child_node("variable_declarators", p[1])
    else:
        tmp = ast.node_create("\,")
        p[0] = ast.three_child_node("variable_declarators", p[1], tmp, p[3])

def p_variable_declarator(p):
    '''variable_declarator : variable_declarator_id
                           | variable_declarator_id EQ variable_initializer'''
    if len(p) == 2:
        p[0] = ast.one_child_node("variable_declarator", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("variable_declarator", p[1], tmp, p[3])

def p_variable_declarator_id(p):
    '''variable_declarator_id : IDENTIFIER'''
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("variable_declarator_id", tmp)

def p_variable_initializer(p):
    '''variable_initializer : expression'''
    p[0] = ast.one_child_node("variable_initializer", p[1])

def p_type(p):
    '''type : primitive_type'''
    p[0] = ast.one_child_node("type", p[1])

def p_primitive_type(p):
    '''primitive_type : BOOLEAN
                      | VOID
                      | SHORT
                      | INT
                      | LONG
                      | CHAR
                      | FLOAT
                      | DOUBLE'''
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("primitive_type", tmp)

# Expressions
def p_expression(p):
    '''expression : logical_expression
                  | logical_expression assignment_operator expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("expression", p[1])
    else:
        p[0] =  ast.three_child_node("expression", p[1], p[2], p[3])

def p_constant_expression(p):
    '''constant_expression : expression'''
    p[0] = ast.one_child_node("constant_expression", tmp)

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
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("assignment_operator", tmp)

def p_par_expression(p):
    '''par_expression : LPAREN expression RPAREN'''
    lparen = ast.node_create(p[1])
    rparen = ast.node_create(p[3])
    p[0] = ast.three_child_node("par_expression", lparen, p[2], rparen)

# Ternary expression grammar not implemented

def p_logical_expression(p):
    '''logical_expression : bitwise_expression
                          | logical_expression AND bitwise_expression
                          | logical_expression OR bitwise_expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("logical_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("logical_expression", p[1], tmp, p[3])

def p_bitwise_expression(p):
    '''bitwise_expression : equality_expression
                          | bitwise_expression BIT_AND equality_expression
                          | bitwise_expression BIT_OR equality_expression
                          | bitwise_expression XOR equality_expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("bitwise_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("bitwise_expression", p[1], tmp, p[3])

def p_equality_expression(p):
    '''equality_expression : comparision_expression
                           | equality_expression EQUALITY comparision_expression
                           | equality_expression NE comparision_expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("equality_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("equality_expression", p[1], tmp, p[3])

def p_comparision_expression(p):
    '''comparision_expression : shift_expression
                              | comparision_expression LE shift_expression
                              | comparision_expression GE shift_expression
                              | comparision_expression LT shift_expression
                              | comparision_expression GT shift_expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("comparison_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("comparison_expression", p[1], tmp, p[3])

def p_shift_expression(p):
    '''shift_expression : additive_expression
                        | shift_expression LSHIFT additive_expression
                        | shift_expression RSHIFT additive_expression
                        | shift_expression RRSHIFT additive_expression'''
    if len(p) == 2:
        p[0] = ast.one_child_node("shift_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("shift_expression", p[1], tmp, p[3])

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''

    if len(p) == 2:
        p[0] = ast.one_child_node("additive_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("additive_expression", p[1], tmp, p[3])

def p_multiplicative_expression(p):
    '''multiplicative_expression : unary_expression
                                 | multiplicative_expression TIMES unary_expression
                                 | multiplicative_expression BY unary_expression'''

    if len(p) == 2:
        p[0] = ast.one_child_node("multiplicative_expression", p[1])
    else:
        tmp = ast.node_create(p[2])
        p[0] = ast.three_child_node("multiplicative_expression", p[1], tmp, p[3])

def p_unary_expression(p):
    '''unary_expression : PLUS unary_expression
                        | MINUS unary_expression
                        | primary'''
    if len(p) == 2:
        p[0] = ast.one_child_node("unary_expression", p[1])
    else:
        tmp = ast.node_create(p[1])
        p[0] = ast.two_child_node("unary_expression", tmp, p[2])

def p_primary(p):
    '''primary : literal
               | par_expression'''
    p[0] = ast.one_child_node("primary", p[1])

def p_primary_identifier(p):
    '''primary : IDENTIFIER'''
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("primary", tmp)

def p_literal(p):
    '''literal : NUMBER'''
    tmp = ast.node_create(p[1])
    p[0] = ast.one_child_node("literal", tmp)

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
   result = parser.parse(s, debug=1)
