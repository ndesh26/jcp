import ptg
import lexer

# Methods
class CompilationUnitParser(object):

    def p_method_type_declaration(self, p):
        '''method_type_declaration : type method_declaration'''
        p[0] = ptg.two_child_node("method_type_declaration", p[1], p[2])

    def p_method_declaration(self, p):
        '''method_declaration : IDENTIFIER method_declarator_rest'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("method_declaration", tmp, p[2])

    def p_method_declarator_rest1(self, p):
        '''method_declarator_rest : formal_parameters SEMICOLON
                                  | formal_parameters exception_throw SEMICOLON'''
        if len(p) == 3:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.two_child_node("method_declarator_rest", p[1], tmp)
        else:
            tmp = ptg.node_create(p[3])
            p[0] = ptg.three_child_node("method_declarator_rest", p[1], p[2], tmp)

    def p_method_declarator_rest2(self, p):
        '''method_declarator_rest : formal_parameters method_body
                                  | formal_parameters exception_throw method_body'''
        if len(p) == 3:
            p[0] = ptg.two_child_node("method_declarator_rest", p[1], p[2])
        else:
            p[0] = ptg.three_child_node("method_declarator_rest", p[1], p[2], p[3])

    def p_formal_pararmeters(self, p):
        '''formal_parameters : LPAREN formal_parameter_decls RPAREN
                             | LPAREN RPAREN'''
        lparen = ptg.node_create(p[1])
        if len(p) == 4:
            rparen = ptg.node_create(p[3])
            p[0] = ptg.three_child_node("formal_parameters", lparen, p[2], rparen)
        else:
            rparen = ptg.node_create(p[2])
            p[0] = ptg.two_child_node("formal_parameters", lparen, rparen)

    def p_formal_parameter_decls(self, p):
        '''formal_parameter_decls : variable_modifiers type formal_parameter_decls_rest
                                  | type formal_parameter_decls_rest'''
        if len(p) == 3:
            p[0] = ptg.two_child_node("formal_paramter_decls", p[1], p[2])
        else:
            p[0] = ptg.three_child_node("formal_parameter_decls", p[1], p[2], p[3])

    def p_formal_parameter_decls_rest(self, p):
        '''formal_parameter_decls_rest : variable_declarator_id
                                       | variable_declarator_id COMMA formal_parameter_decls
                                       | DOT DOT DOT variable_declarator_id'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("formal_parameter_decls_rest", p[1])
        elif len(p) == 4:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("formal_parameter_decls_rest", p[1], tmp, p[3])
        else:
            tmp = ptg.node_create("...")
            p[0] = ptg.two_child_node("formal_paramater_decls_rest", tmp, p[2])

    def p_method_body(self, p):
        '''method_body : block'''
        p[0] = ptg.one_child_node("method_body", p[1])

    def p_constructor_body(self, p):
        '''constructor_body : block'''
        p[0] = ptg.one_child_node("constructor_body", p[1])

    # Exceptions
    def p_exception_throw(self, p):
        '''exception_throw : THROWS qualified_name_list'''
        tmp = ptg.node_create("throws")
        p[0] = ptg.two_child_node("exception_throw", p[1], tmp, p[3])

    def p_qualified_name_list(self, p):
        '''qualified_name_list : qualified_name
                               | qualified_name COMMA qualified_name_list'''
        tmp = ptg.node_create("\,")
        if len(p) == 2:
            p[0] = ptg.one_child_node("qualified_name_list", p[1])
        else:
            p[0] = ptg.three_child_node("qualified_name_list", p[1], tmp, p[3])

    def p_qualified_name(self, p):
        '''qualified_name : IDENTIFIER
                          | IDENTIFIER DOT qualified_name'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("qualified_name", p[1])
        else:
            tmp = ptg.node_create(".")
            p[0] = ptg.three_child_node("qualified_name", p[1], tmp, p[3])

# Statements
class StatementParser(object):

    def p_block(self, p):
        '''block : LBRACE block_statements RBRACE
                 | LBRACE RBRACE'''
        lbrace = ptg.node_create(p[1])
        if len(p) == 3:
            rbrace = ptg.node_create(p[2])
            p[0] = ptg.two_child_node("block", lbrace, rbrace)
        else:
            rbrace = ptg.node_create(p[3])
            p[0] = ptg.three_child_node("block", lbrace, p[2], rbrace)

    def p_block_statements(self, p):
        '''block_statements : block_statement
                            | block_statements block_statement'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("block_statements", p[1])
        else:
            p[0] = ptg.two_child_node("block_statements", p[1], p[2])

    def p_block_statement(self, p):
        '''block_statement : local_variable_declaration_statement
                           | statement'''
        p[0] = ptg.one_child_node("block_statement", p[1])

    def p_local_variable_declaration_statement(self, p):
        '''local_variable_declaration_statement : local_variable_declaration SEMICOLON'''
        tmp = ptg.node_create(p[2])
        p[0] = ptg.two_child_node("local_variable_declaration_statement", p[1], tmp)

    def p_local_variable_declaration(self, p):
        '''local_variable_declaration : type variable_declarators
                                      | variable_modifiers type variable_declarators'''
        if len(p) == 3:
            p[0] = ptg.two_child_node("local_variable_declaration", p[1], p[2])
        else:
            p[0] = ptg.three_child_node("local_variable_declaration", p[1], p[2], p[3])

    def p_variable_modfiers(self, p):
        '''variable_modifiers : variable_modifier
                              | variable_modifiers variable_modifier'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("variable_modifiers", p[1])
        else:
            p[0] = ptg.two_child_node("variable_modifiers", p[1], p[2])

    def p_variable_modifier(self, p):
        '''variable_modifier : FINAL'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("variable_modifier", tmp)

    def p_statement_rule1(self, p):
        '''statement : block
                     | expression SEMICOLON
                     | WHILE par_expression statement
                     | IF par_expression statement
                     | DO statement WHILE par_expression SEMICOLON'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("statement", p[1])
        elif len(p) == 3:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.two_child_node("statement", p[1], tmp)
        elif len(p) == 4:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.three_child_node("statement", tmp, p[2], p[3])
        elif len(p) == 6:
            tmp1 = ptg.node_create(p[1])
            tmp2 = ptg.node_create(p[3])
            tmp3 = ptg.node_create(p[5])
            p[0] = ptg.five_child_node("statement", tmp1, p[2], tmp2, p[4], tmp3)

    def p_statement_rule2(self, p):
        '''statement : RETURN SEMICOLON
                     | RETURN expression SEMICOLON'''
        tmp1 = ptg.node_create(p[1])
        tmp2 = ptg.node_create(";")
        if len(p) == 3:
            p[0] = ptg.two_child_node("statement", tmp1, tmp2)
        elif len(p) == 4:
            p[0] = ptg.three_child_node("statement", tmp1, p[2], tmp2)

    def p_statement_rule3(self, p):
        '''statement : SEMICOLON'''
        tmp = ptg.node_create(";")
        p[0] = ptg.two_child_node("statement", tmp)

    def p_statement_rule4(self, p):
        '''statement : IF par_expression statement ELSE statement'''
        if len(p) == 6:
            tmp1 = ptg.node_create(p[1])
            tmp2 = ptg.node_create(p[4])
            p[0] = ptg.five_child_node("statement", tmp1, p[2], p[3], tmp2, p[5])

    def p_variable_declarators(self, p):
        '''variable_declarators : variable_declarator
                                | variable_declarators COMMA variable_declarator'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("variable_declarators", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("variable_declarators", p[1], tmp, p[3])

    def p_variable_declarator(self, p):
        '''variable_declarator : variable_declarator_id
                               | variable_declarator_id EQ variable_initializer'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("variable_declarator", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("variable_declarator", p[1], tmp, p[3])

    def p_variable_declarator_id(self, p):
        '''variable_declarator_id : IDENTIFIER'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("variable_declarator_id", tmp)

    def p_variable_initializer(self, p):
        '''variable_initializer : expression'''
        p[0] = ptg.one_child_node("variable_initializer", p[1])

    def p_type(self, p):
        '''type : primitive_type'''
        p[0] = ptg.one_child_node("type", p[1])

    def p_primitive_type(self, p):
        '''primitive_type : BOOLEAN
                          | VOID
                          | SHORT
                          | INT
                          | LONG
                          | CHAR
                          | FLOAT
                          | DOUBLE'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("primitive_type", tmp)

# Expressions
class ExpressionParser(object):

    def p_expression(self, p):
        '''expression : logical_expression
                      | logical_expression assignment_operator expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("expression", p[1])
        else:
            p[0] =  ptg.three_child_node("expression", p[1], p[2], p[3])

    def p_constant_expression(self, p):
        '''constant_expression : expression'''
        p[0] = ptg.one_child_node("constant_expression", tmp)

    def p_assignment_operator(self, p):
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
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("assignment_operator", tmp)

    def p_par_expression(self, p):
        '''par_expression : LPAREN expression RPAREN'''
        lparen = ptg.node_create(p[1])
        rparen = ptg.node_create(p[3])
        p[0] = ptg.three_child_node("par_expression", lparen, p[2], rparen)

    # Ternary expression grammar not implemented

    def p_logical_expression(self, p):
        '''logical_expression : bitwise_expression
                              | logical_expression AND bitwise_expression
                              | logical_expression OR bitwise_expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("logical_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("logical_expression", p[1], tmp, p[3])

    def p_bitwise_expression(self, p):
        '''bitwise_expression : equality_expression
                              | bitwise_expression BIT_AND equality_expression
                              | bitwise_expression BIT_OR equality_expression
                              | bitwise_expression XOR equality_expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("bitwise_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("bitwise_expression", p[1], tmp, p[3])

    def p_equality_expression(self, p):
        '''equality_expression : comparision_expression
                               | equality_expression EQUALITY comparision_expression
                               | equality_expression NE comparision_expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("equality_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("equality_expression", p[1], tmp, p[3])

    def p_comparision_expression(self, p):
        '''comparision_expression : shift_expression
                                  | comparision_expression LE shift_expression
                                  | comparision_expression GE shift_expression
                                  | comparision_expression LT shift_expression
                                  | comparision_expression GT shift_expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("comparison_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("comparison_expression", p[1], tmp, p[3])

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression
                            | shift_expression RRSHIFT additive_expression'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("shift_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("shift_expression", p[1], tmp, p[3])

    def p_additive_expression(self, p):
        '''additive_expression : multiplicative_expression
                               | additive_expression PLUS multiplicative_expression
                               | additive_expression MINUS multiplicative_expression'''

        if len(p) == 2:
            p[0] = ptg.one_child_node("additive_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("additive_expression", p[1], tmp, p[3])

    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : unary_expression
                                     | multiplicative_expression TIMES unary_expression
                                     | multiplicative_expression BY unary_expression'''

        if len(p) == 2:
            p[0] = ptg.one_child_node("multiplicative_expression", p[1])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("multiplicative_expression", p[1], tmp, p[3])

    def p_unary_expression(self, p):
        '''unary_expression : PLUS unary_expression
                            | MINUS unary_expression
                            | primary'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("unary_expression", p[1])
        else:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.two_child_node("unary_expression", tmp, p[2])

    def p_primary(self, p):
        '''primary : literal
                   | par_expression'''
        p[0] = ptg.one_child_node("primary", p[1])

    def p_primary_identifier(self, p):
        '''primary : IDENTIFIER'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("primary", tmp)

    def p_literal(self, p):
        '''literal : NUMBER'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("literal", tmp)

class JavaParser(ExpressionParser, StatementParser, CompilationUnitParser):
    tokens = lexer.tokens

    def p_goal_compilation_unit(self, p):
        '''goal : INCR method_type_declaration'''
        p[0] = p[2]

    def p_goal_expression(self, p):
        '''goal : DECR expression'''
        p[0] = p[2]

    def p_goal_statement(self, p):
        '''goal : TIMES TIMES block_statement'''
        p[0] = p[2]

    # Error rule for syntax errors
    def p_error(self, p):
        print('error: {}'.format(p))

    def p_empty(self, p):
        '''empty :'''
