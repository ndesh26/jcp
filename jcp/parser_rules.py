import ptg
import lexer
import symbol_table as st
import pydot
from ast import literal_eval

ast = ""
symbol_table = st.SymbolTable()
symbol_table.insert('printInt', {'value': 'printInt', 'type':'void (int)', 'modifiers': ''})
symbol_table.insert('printlnInt', {'value': 'printlnInt', 'type':'void (int)', 'modifiers': ''})
symbol_table.insert('scanInt', {'value': 'scanInt', 'type':'int ()', 'modifiers': ''})
nat = []

class Node:
    def __init__(self, name="", value="", type="", children=None, modifiers=None, dims=0, arraylen=None, sym_entry=None, lineno=0):
        self.name = name
        self.value = value
        self.type = type
        self.dims = dims
        self.lineno = lineno
        self.sym_entry = sym_entry
        if modifiers:
            self.modifiers = modifiers
        else:
            self.modifiers = [ ]
        if children:
             self.children = children
        else:
             self.children = [ ]
        if arraylen:
            self.arraylen = arraylen
        else:
            self.arraylen = [ ]

    def print_tree(self, k=1):
        global ast
        global nat
        if self.name:
            ast = ast + self.name + " " + self.type + " " + "{}".format(self.value)
            if self.name == "DeclsRefExpr":
                for length in self.arraylen:
                    ast += "[{}]".format(length)
            for modifier in self.modifiers:
                if modifier:
                    ast = ast + " " + modifier
            ast = ast + "\n"
            if self.children == [  ]:
                return
            else:
                for node in self.children:
                    nat.append(1)
                    if isinstance(node, Node):
                        if node.name:
                            if node == self.children[len(self.children) - 1]:
                                for i in nat[:k-1]:
                                    if i == 1:
                                        ast = ast + ' |'
                                    elif i == 0:
                                        ast = ast + '  '
                                ast = ast + ' `-'
                                nat[k-1] = 0
                            else:
                                for i in nat[:k-1]:
                                    if i == 1:
                                        ast = ast + ' |'
                                    elif i == 0:
                                        ast = ast + '  '
                                ast = ast + ' |-'
                                nat[k-1] = 1
                            node.print_tree(k+1)
                    else:
                        print("Error {}".format(node))

    def print_dot(self, graph, id=0):
        parent = pydot.Node(id, label=self.name + "\n" + "{}".format(self.value))
        id += 1
        graph.add_node(parent)
        for node in self.children:
            if isinstance(node, Node):
                if node.name:
                    (child,id) = node.print_dot(graph, id)
                    graph.add_edge(pydot.Edge(parent, child))
        return (parent,id)

    def print_png(self):
        graph = pydot.Dot(graph_type='graph')
        self.print_dot(graph=graph)
        graph.write_png('out.png')


def check_type(name, type, node):
    if node.name == "InitListExpr":
        for node1 in node.children:
            check_type(name, type, node1)
    else:
        if node.type != type:
            print("line {}: array '{}' (type '{}') initialized to value '{}' of type '{}'".format(node.lineno, name, type, node.value, node.type))


class ExpressionParser(object):

    def p_expression(self, p):
        '''expression : assignment_expression'''
        p[0] = p[1]

    def p_expression_not_name(self, p):
        '''expression_not_name : assignment_expression_not_name'''
        p[0] = p[1]

    def p_assignment_expression(self, p):
        '''assignment_expression : assignment
                                 | conditional_expression'''
        p[0] = p[1]

    def p_assignment_expression_not_name(self, p):
        '''assignment_expression_not_name : assignment
                                          | conditional_expression_not_name'''
        p[0] = p[1]

    def p_assignment(self, p):
        '''assignment : postfix_expression assignment_operator assignment_expression'''
        if p[1].type == "error":
            p[0] = Node("BinaryOperator", value=p[2].value, type="error", children=[p[1], p[3]])
        elif p[1].type == p[3].type and p[1].dims == 0:
            p[0] = Node("BinaryOperator", value=p[2].value, children=[p[1], p[3]])
        else:
            print("line {}: Type mismatch".format(p[2].lineno))
            p[0] = Node("BinaryOperator", value=p[2].value, type="error", children=[p[1], p[3]])

    def p_assignment_operator(self, p):
        '''assignment_operator : '='
                               | TIMES_ASSIGN
                               | DIVIDE_ASSIGN
                               | REMAINDER_ASSIGN
                               | PLUS_ASSIGN
                               | MINUS_ASSIGN
                               | LSHIFT_ASSIGN
                               | RSHIFT_ASSIGN
                               | RRSHIFT_ASSIGN
                               | AND_ASSIGN
                               | OR_ASSIGN
                               | XOR_ASSIGN'''
        p[0] = Node(value=p[1], lineno=p.lineno(1))

    def p_conditional_expression(self, p):
        '''conditional_expression : conditional_or_expression
                                  | conditional_or_expression '?' expression ':' conditional_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 6:
            if p[3].type == p[5].type:
                p[0] = Node("ConditionalOperator", value="", type=p[3].type, children=[p[1], p[3], p[5]])
            elif p[3].type == "string" or p[3].type == "float" or p[3].type == "char":
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[5] = Node("ImplicitCastExpr", type=p[3].type, children=p[5])
                p[0] = Node("ConditionalOperator", value="", type=p[3].type, children=[p[1], p[3], p[5]])
            elif p[5].type == "string" or p[5].type == "float" or p[5].type == "char":
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[3] = Node("ImplicitCastExpr", type=p[5].type, children=[p[3]])
                p[0] = Node("ConditionalOperator", value="", type=p[5].type, children=[p[1], p[3], p[5]])
            else:
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[0] = Node("ConditionalOperator", value="", type="error", children=[p[1], p[3], p[5]])


    def p_conditional_expression_not_name(self, p):
        '''conditional_expression_not_name : conditional_or_expression_not_name
                                           | conditional_or_expression_not_name '?' expression ':' conditional_expression
                                           | name '?' expression ':' conditional_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 6:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[3].type == p[5].type:
                p[0] = Node("ConditionalOperator", value="", type=p[3].type, children=[p[1], p[3], p[5]])
            elif p[3].type == "string" or p[3].type == "float" or p[3].type == "char":
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[5] = Node("ImplicitCastExpr", type=p[3].type, children=p[5])
                p[0] = Node("ConditionalOperator", value="", type=p[3].type, children=[p[1], p[3], p[5]])
            elif p[5].type == "string" or p[5].type == "float" or p[5].type == "char":
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[3] = Node("ImplicitCastExpr", type=p[5].type, children=[p[3]])
                p[0] = Node("ConditionalOperator", value="", type=p[5].type, children=[p[1], p[3], p[5]])
            else:
                print("line {}: type mismatch in conditional expression".format(p.lineno(2)))
                p[0] = Node("ConditionalOperator", value="", type="error", children=[p[1], p[3], p[5]])

    def p_conditional_or_expression(self, p):
        '''conditional_or_expression : conditional_and_expression
                                     | conditional_or_expression OR conditional_and_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])

    def p_conditional_or_expression_not_name(self, p):
        '''conditional_or_expression_not_name : conditional_and_expression_not_name
                                              | conditional_or_expression_not_name OR conditional_and_expression
                                              | name OR conditional_and_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])

    def p_conditional_and_expression(self, p):
        '''conditional_and_expression : inclusive_or_expression
                                      | conditional_and_expression AND inclusive_or_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])

    def p_conditional_and_expression_not_name(self, p):
        '''conditional_and_expression_not_name : inclusive_or_expression_not_name
                                               | conditional_and_expression_not_name AND inclusive_or_expression
                                               | name AND inclusive_or_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])


    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_inclusive_or_expression_not_name(self, p):
        '''inclusive_or_expression_not_name : exclusive_or_expression_not_name
                                            | inclusive_or_expression_not_name '|' exclusive_or_expression
                                            | name '|' exclusive_or_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression : and_expression
                                   | exclusive_or_expression '^' and_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_exclusive_or_expression_not_name(self, p):
        '''exclusive_or_expression_not_name : and_expression_not_name
                                            | exclusive_or_expression_not_name '^' and_expression
                                            | name '^' and_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_and_expression(self, p):
        '''and_expression : equality_expression
                          | and_expression '&' equality_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_and_expression_not_name(self, p):
        '''and_expression_not_name : equality_expression_not_name
                                   | and_expression_not_name '&' equality_expression
                                   | name '&' equality_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[1].type in ["int", "char"] and p[3].type in ["int", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_equality_expression(self, p):
        '''equality_expression : instanceof_expression
                               | equality_expression EQ instanceof_expression
                               | equality_expression NEQ instanceof_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])

    def p_equality_expression_not_name(self, p):
        '''equality_expression_not_name : instanceof_expression_not_name
                                        | equality_expression_not_name EQ instanceof_expression
                                        | name EQ instanceof_expression
                                        | equality_expression_not_name NEQ instanceof_expression
                                        | name NEQ instanceof_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])

    def p_instanceof_expression(self, p):
        '''instanceof_expression : relational_expression
                                 | instanceof_expression INSTANCEOF reference_type'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = Node("BinaryOperator", value=p[2], type="", children=[p[1], p[3]])

    def p_instanceof_expression_not_name(self, p):
        '''instanceof_expression_not_name : relational_expression_not_name
                                          | name INSTANCEOF reference_type
                                          | instanceof_expression_not_name INSTANCEOF reference_type'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            p[0] = Node("BinaryOperator", value=p[2], type="", children=[p[1], p[3]])

    def p_relational_expression(self, p):
        '''relational_expression : shift_expression
                                 | relational_expression '>' shift_expression
                                 | relational_expression '<' shift_expression
                                 | relational_expression GTEQ shift_expression
                                 | relational_expression LTEQ shift_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type in ["int", "float", "char"] and p[3].type in ["int", "float", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_relational_expression_not_name(self, p):
        '''relational_expression_not_name : shift_expression_not_name
                                          | shift_expression_not_name '<' shift_expression
                                          | name '<' shift_expression
                                          | shift_expression_not_name '>' shift_expression
                                          | name '>' shift_expression
                                          | shift_expression_not_name GTEQ shift_expression
                                          | name GTEQ shift_expression
                                          | shift_expression_not_name LTEQ shift_expression
                                          | name LTEQ shift_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[1].type in ["int", "float", "char"] and p[3].type in ["int", "float", "char"]:
                p[0] = Node("BinaryOperator", value=p[2], type="bool", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression
                            | shift_expression RRSHIFT additive_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "char" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="char", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_shift_expression_not_name(self, p):
        '''shift_expression_not_name : additive_expression_not_name
                                     | shift_expression_not_name LSHIFT additive_expression
                                     | name LSHIFT additive_expression
                                     | shift_expression_not_name RSHIFT additive_expression
                                     | name RSHIFT additive_expression
                                     | shift_expression_not_name RRSHIFT additive_expression
                                     | name RRSHIFT additive_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                    p[1].type = "error"
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "char" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="char", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_additive_expression(self, p):
        '''additive_expression : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif (p[1].type == "float" and p[3].type == "int") or (p[1].type == "int" and p[3].type == "float"):
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "float":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_additive_expression_not_name(self, p):
        '''additive_expression_not_name : multiplicative_expression_not_name
                                        | additive_expression_not_name '+' multiplicative_expression
                                        | name '+' multiplicative_expression
                                        | additive_expression_not_name '-' multiplicative_expression
                                        | name '-' multiplicative_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                    p[1].type = "error"
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif (p[1].type == "float" and p[3].type == "int") or (p[1].type == "int" and p[3].type == "float"):
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "float":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : unary_expression
                                     | multiplicative_expression '*' unary_expression
                                     | multiplicative_expression '/' unary_expression
                                     | multiplicative_expression '%' unary_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif (p[1].type == "float" and p[3].type == "int") or (p[1].type == "int" and p[3].type == "float"):
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "float":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])


    def p_multiplicative_expression_not_name(self, p):
        '''multiplicative_expression_not_name : unary_expression_not_name
                                              | multiplicative_expression_not_name '*' unary_expression
                                              | name '*' unary_expression
                                              | multiplicative_expression_not_name '/' unary_expression
                                              | name '/' unary_expression
                                              | multiplicative_expression_not_name '%' unary_expression
                                              | name '%' unary_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1].type == "":
                entry = symbol_table.get_entry(p[1].value)
                if entry:
                    p[1].type = entry['type']
                    p[1].dims = entry['dims']
                    p[1].arraylen = entry['arraylen']
                    p[1].modifiers = entry['modifiers']
                    p[1].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                    p[1].type = "error"
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Node("BinaryOperator", value=p[2], type="int", children=[p[1], p[3]])
            elif (p[1].type == "float" and p[3].type == "int") or (p[1].type == "int" and p[3].type == "float"):
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            elif p[1].type == "float" and p[3].type == "float":
                p[0] = Node("BinaryOperator", value=p[2], type="float", children=[p[1], p[3]])
            else:
                print("line {}: incompatible operator '{}' with operand of type '{}' and '{}'".format(p.lineno(2), p[2], p[1].type, p[3].type))
                p[0] = Node("BinaryOperator", value=p[2], type="error", children=[p[1], p[3]])

    def p_unary_expression(self, p):
        '''unary_expression : pre_increment_expression
                            | pre_decrement_expression
                            | '+' unary_expression
                            | '-' unary_expression
                            | unary_expression_not_plus_minus'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node("UnaryOperator", value=p[1], type=p[2].type, children=[p[2]])

    def p_unary_expression_not_name(self, p):
        '''unary_expression_not_name : pre_increment_expression
                                     | pre_decrement_expression
                                     | '+' unary_expression
                                     | '-' unary_expression
                                     | unary_expression_not_plus_minus_not_name'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node("UnaryOperator", value=p[1], type=p[2].type, children=[p[2]])

    def p_pre_increment_expression(self, p):
        '''pre_increment_expression : PLUSPLUS unary_expression'''
        p[0] = Node("UnaryOperator", value="pre"+p[1], type=p[2].type, children=[p[2]])

    def p_pre_decrement_expression(self, p):
        '''pre_decrement_expression : MINUSMINUS unary_expression'''
        p[0] = Node("UnaryOperator", value="pre"+p[1], type=p[2].type, children=[p[2]])

    def p_unary_expression_not_plus_minus(self, p):
        '''unary_expression_not_plus_minus : postfix_expression
                                           | '~' unary_expression
                                           | '!' unary_expression
                                           | cast_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node("UnaryOperator", value=p[1], type=p[2].type, children=[p[2]])

    def p_unary_expression_not_plus_minus_not_name(self, p):
        '''unary_expression_not_plus_minus_not_name : postfix_expression_not_name
                                                    | '~' unary_expression
                                                    | '!' unary_expression
                                                    | cast_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node("UnaryOperator", value=p[1], type=p[2].type, children=[p[2]])

    def p_postfix_expression(self, p):
        '''postfix_expression : primary
                              | name
                              | post_increment_expression
                              | post_decrement_expression'''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p[1].lineno, p[1].value))
                p[1].type = "error"
        p[0] = p[1]

    def p_postfix_expression_not_name(self, p):
        '''postfix_expression_not_name : primary
                                       | post_increment_expression
                                       | post_decrement_expression'''
        p[0] = p[1]

    def p_post_increment_expression(self, p):
        '''post_increment_expression : postfix_expression PLUSPLUS'''
        p[0] = Node("UnaryOperator", value="post"+p[2], type=p[1].type, children=[p[1]])

    def p_post_decrement_expression(self, p):
        '''post_decrement_expression : postfix_expression MINUSMINUS'''
        p[0] = Node("UnaryOperator", value="post"+p[2], type=p[1].type, children=[p[1]])

    def p_primary(self, p):
        '''primary : primary_no_new_array
                   | array_creation_with_array_initializer
                   | array_creation_without_array_initializer'''
        p[0] = p[1]

    def p_primary_no_new_array(self, p):
        '''primary_no_new_array : literal
                                | class_instance_creation_expression
                                | field_access
                                | method_invocation
                                | array_access'''
        p[0] = p[1]

    def p_primary_no_new_array2(self, p):
        '''primary_no_new_array : '(' name ')'
                                | THIS
                                | '(' expression_not_name ')' '''
        if len(p) == 2:
            p[0] = Node("DeclsRefExpr", value='this')
        elif len(p) == 4:
            if p[2].type == "":
                entry = symbol_table.get_entry(p[2].value)
                if entry:
                    p[2].type = entry['type']
                    p[2].dims = entry['dims']
                    p[2].arraylen = entry['arraylen']
                    p[2].modifiers = entry['modifiers']
                    p[2].sym_entry = entry
                else:
                    print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[2].value))
                    p[2].type = "error"
            p[0] = p[2]

    def p_primary_no_new_array3(self, p):
        '''primary_no_new_array : name '.' THIS
                                | name '.' SUPER'''
        # TODO: Not yet implemented
        p[0] = Node("Modifier", p[3], "", [])

    def p_primary_no_new_array4(self, p):
        '''primary_no_new_array : name '.' CLASS
                                | name dims '.' CLASS
                                | primitive_type dims '.' CLASS
                                | primitive_type '.' CLASS'''
        # TODO: Not yet implemented
        p[0] = Node("Modifier", p[3], "", [])

    def p_dims_opt(self, p):
        '''dims_opt : dims'''
        p[0] = p[1]

    def p_dims_opt2(self, p):
        '''dims_opt : empty'''
        p[0] = p[1]

    def p_dims(self, p):
        '''dims : dims_loop'''
        p[0] = p[1]

    def p_dims_loop(self, p):
        '''dims_loop : one_dim_loop
                     | dims_loop one_dim_loop'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[1].dims = p[1].dims + 1
            p[0] = p[1]

    def p_one_dim_loop(self, p):
        '''one_dim_loop : '[' ']' '''
        p[0] = Node(dims=1)

    def p_cast_expression(self, p):
        '''cast_expression : '(' primitive_type dims_opt ')' unary_expression'''
        p[0] = Node("CastExpr", type=p[2], children=[p[5]], dims=p[3].dims)

    def p_cast_expression2(self, p):
        '''cast_expression : '(' name type_arguments dims_opt ')' unary_expression_not_plus_minus'''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                p[1].type = "error"
        p[0] = Node("CastExpr", type=p[2].value+p[3], children=[p[6]], dims=p[4].dims)

    def p_cast_expression3(self, p):
        '''cast_expression : '(' name type_arguments '.' class_or_interface_type dims_opt ')' unary_expression_not_plus_minus'''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                p[1].type = "error"
        p[0] = Node("CastExpr", type=p[2].value+p[3]+p[5], children=[p[8]], dims=p[6].dims)

    def p_cast_expression4(self, p):
        '''cast_expression : '(' name ')' unary_expression_not_plus_minus'''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                p[1].type = "error"
        p[0] = Node("CastExpr", type=p[2].value, children=[p[4]])

    def p_cast_expression5(self, p):
        '''cast_expression : '(' name dims ')' unary_expression_not_plus_minus'''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(1), p[1].value))
                p[1].type = "error"
        p[0] = Node("CastExpr", type=p[2].value, children=[p[5]], dims=p[3].dims)

class StatementParser(object):

    def p_block(self, p):
        '''block : begin_scope '{' block_statements_opt '}' end_scope '''
        p[0] = p[3]

    def p_block_statements_opt(self, p):
        '''block_statements_opt : block_statements'''
        p[0] = p[1]

    def p_block_statements_opt2(self, p):
        '''block_statements_opt : empty'''
        p[0] = p[1]

    def p_block_statements(self, p):
        '''block_statements : block_statement
                            | block_statements block_statement'''
        if len(p) == 2:
            p[0] = Node("BlockStmts", children=[p[1]])
            if (p[1].type == "error"):
                p[0].type = "error"
            if p[1].name == "ReturnStmt":
                p[0].value=1
        elif len(p) == 3:
            if (p[2].type == "error"):
                p[1].type = "error"
            if p[2].name == "ReturnStmt":
                p[1].value=1
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_block_statement(self, p):
        '''block_statement : local_variable_declaration_statement
                           | statement
                           | class_declaration
                           | interface_declaration
                           | annotation_type_declaration
                           | enum_declaration'''
        p[0] = p[1]

    def p_local_variable_declaration_statement(self, p):
        '''local_variable_declaration_statement : local_variable_declaration ';' '''
        p[1].name = "DeclStmt"
        p[0] = p[1]

    def p_local_variable_declaration(self, p):
        '''local_variable_declaration : type variable_declarators'''
        for node in p[2].children:
            if (node.type != "") and (node.type == "" or node.type != p[1].type):
                print("line {}: variable '{}' (type '{}') initialized to type '{}'".format(node.lineno, node.value, p[1].type, node.type))
                p[2].type = "error"
            node.type = p[1].type
            if node.dims == 0:
                node.dims = p[1].dims
            if node.dims != p[1].dims and p[1].dims != 0:
                print("line {}: variable '{}'  is a {}-D array, but initialized using a {}-D initializer".format(node.lineno, node.value, node.dims, p[1].dims))
            if node.children != [  ] and node.children[0].name == "InitListExpr":
                check_type(node.value, node.type, node.children[0])
            entry = symbol_table.get_entry(node.value)
            if entry:
                print("line {}: variable '{}' is already declared".format(node.lineno, node.value))
            else:
                node.sym_entry = symbol_table.insert(node.value, {'value': node.value, 'type':node.type, 'dims':node.dims, 'arraylen':node.arraylen, 'modifiers':[]})
                node.sym_entry['offset'] = symbol_table.get_arg_size() - node.sym_entry['offset'] - st.type_width(node.sym_entry)
        p[0] = p[2]

    def p_local_variable_declaration2(self, p):
        '''local_variable_declaration : modifiers type variable_declarators'''
        for node in p[3].children:
            if (node.type != "") and (node.type == "" or node.type != p[2].type):
                print("line {}: variable '{}' (type '{}') initialized to type '{}'".format(node.lineno, node.value, p[2].type, node.type))
                p[3].type = "error"
            node.type = p[2].type
            node.modifiers = p[1].modifiers
            if symbol_table.get_entry(node.value):
                print("line {}: variable '{}' is already declared".format(node.lineno, node.value))
            else:
                node.sym_entry = symbol_table.insert(node.value, {'value': node.value, 'type':node.type, 'modifiers':node.modifiers, 'dims':node.dims, 'arraylen':node.arraylen})
        p[0] = p[3]

    def p_variable_declarators(self, p):
        '''variable_declarators : variable_declarator
                                | variable_declarators ',' variable_declarator'''
        if len(p) == 2:
            p[0] = Node("Decls", type=p[1].type, children=[p[1]])
        elif len(p) == 4:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_variable_declarator(self, p):
        '''variable_declarator : variable_declarator_id
                               | variable_declarator_id '=' variable_initializer'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[1].type = p[3].type
            p[1].arraylen = p[3].arraylen
            p[1].children.append(p[3])
            p[1].lineno = p.lineno(2)
            p[0] = p[1]

    def p_variable_declarator_id(self, p):
        '''variable_declarator_id : NAME dims_opt'''
        p[0] = Node("VarDecl", value=p[1], dims=p[2].dims)

    def p_variable_initializer(self, p):
        '''variable_initializer : expression
                                | array_initializer'''
        p[0] = p[1]

    def p_statement(self, p):
        '''statement : statement_without_trailing_substatement
                     | labeled_statement
                     | if_then_statement
                     | if_then_else_statement
                     | while_statement
                     | for_statement
                     | enhanced_for_statement'''
        p[0] = p[1]

    def p_statement_without_trailing_substatement(self, p):
        '''statement_without_trailing_substatement : block
                                                   | expression_statement
                                                   | assert_statement
                                                   | empty_statement
                                                   | switch_statement
                                                   | do_statement
                                                   | break_statement
                                                   | continue_statement
                                                   | return_statement
                                                   | synchronized_statement
                                                   | throw_statement
                                                   | try_statement
                                                   | try_statement_with_resources'''
        p[0] = p[1]

    def p_expression_statement(self, p):
        '''expression_statement : statement_expression ';'
                                | explicit_constructor_invocation'''
        p[0] = p[1]

    def p_statement_expression(self, p):
        '''statement_expression : assignment
                                | pre_increment_expression
                                | pre_decrement_expression
                                | post_increment_expression
                                | post_decrement_expression
                                | method_invocation
                                | class_instance_creation_expression'''
        p[0] = p[1]

    def p_comma_opt(self, p):
        '''comma_opt : ','
                     | empty'''
        pass

    def p_array_initializer(self, p):
        '''array_initializer : '{' comma_opt '}' '''
        p[0] = Node("InitListExpr", arraylen=[0], dims=1)

    def p_array_initializer2(self, p):
        '''array_initializer : '{' variable_initializers '}'
                             | '{' variable_initializers ',' '}' '''
        p[0] = p[2]

    def p_variable_initializers(self, p):
        '''variable_initializers : variable_initializer
                                 | variable_initializers ',' variable_initializer'''
        if len(p) == 2:
            p[0] = Node("InitListExpr", arraylen=[1]+p[1].arraylen, children=[p[1]], dims=p[1].dims+1)
        elif len(p) == 4:
            p[1].children.append(p[3])
            p[1].arraylen[0] += 1
            p[0] = p[1]

    def p_method_invocation(self, p):
        '''method_invocation : NAME '(' argument_list_opt ')' '''
        entry = symbol_table.get_entry(p[1])
        if entry:
            p[1] = Node("DeclsRefExpr", value=p[1], type=entry['type'], modifiers=entry['modifiers'], sym_entry=entry)
            p[3].children = [Node("DeclsRefExpr", value='this', sym_entry=symbol_table.get_entry('this'))]+ p[3].children
            p[0] = Node("MethodInvocation", children=[p[1]]+p[3].children)
            p[0].type = p[1].type.split(" ", 1)[0]
            args = p[1].type.split(" ", 1)[1][1:-1].split(",", len(p[3].children)-1)
            for arg, node in zip(args[1:], p[3].children[1:]):
                if arg != node.type:
                    print("line {}: the function is expecting arg of type '{}' but the arg provided is of type '{}'".format(p.lineno(1), arg, node.type))
        else:
            print("line {}: the method '{}' has not been declared in this scope".format(p.lineno(2), p[1]))
            p[1] = Node("DeclsRefExpr", value=p[1], type="error")
            p[0] = Node("MethodInvocation", children=[p[1]]+p[3].children)

    def p_method_invocation2(self, p):
        '''method_invocation : name '.' type_arguments NAME '(' argument_list_opt ')'
                             | primary '.' type_arguments NAME '(' argument_list_opt ')' '''
        # TODO: Not implemented

    def p_method_invocation3(self, p):
        '''method_invocation : SUPER '.' type_arguments NAME '(' argument_list_opt ')' '''
        # TODO: Not implemented

    def p_method_invocation4(self, p):
        '''method_invocation : name '.' NAME '(' argument_list_opt ')'
                             | primary '.' NAME '(' argument_list_opt ')' '''
        entry = symbol_table.get_entry(p[1].value)
        if entry:
            p[1].type = entry['type']
            p[1].dims = entry['dims']
            p[1].arraylen = entry['arraylen']
            p[1].modifiers = entry['modifiers']
            p[1].sym_entry = entry
            entry = symbol_table.lookup_method(p[1].type, p[3])
            if entry:
                p[3] = Node("ObjectMethodExpr", value=p[2]+p[3], children=[p[1]], type=entry['type'], sym_entry=entry)
                p[5].children = [p[1]]+ p[5].children
                p[0] = Node("MethodInvocation", children=[p[3]]+p[5].children)
                p[0].type = p[3].type.split(" ", 1)[0]
                args = p[3].type.split(" ", 1)[1][1:-1].split(",", len(p[5].children)-1)
                for arg, node in zip(args[1:], p[5].children[1:]):
                    if arg != node.type:
                        print("line {}: the function is expecting arg of type '{}' but the arg provided is of type '{}'".format(p.lineno(2), arg, node.type))
            else:
                print("line {}: there is no method named '{}' for object of type '{}'".format(p.lineno(2), p[3], p[1].type))
                p[3] = Node("ObjectMethodExpr", value=p[2]+p[3], children=[p[1]], type="error")
                p[0] = Node("MethodInvocation", children=[p[3]]+p[5].children)
        else:
            print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
            p[1].type="error"
            p[3] = Node("ObjectMethodExpr", value=p[2]+p[3], children=[p[1]])
            p[0] = Node("MethodInvocation", children=[p[3]]+p[5].children)

    def p_method_invocation5(self, p):
        '''method_invocation : SUPER '.' NAME '(' argument_list_opt ')' '''
        p[1] = Node("RefExpr", value=p[1])
        entry = symbol_table.get_entry(p[1].value+p[2]+p[3])
        if entry:
            p[3] = Node("MemberExpr", value=p[2]+p[3], children=[p[1]], type=entry['type'])
        else:
            print("line {}: the method '{}' has not been declared in this scope".format(p.lineno(2), p[1]))
            p[3] = Node("MemberExpr", value=p[2]+p[3], children=[p[1]])
        p[0] = Node("MethodInvocation", children=[p[3]]+p[5].children)

    def p_labeled_statement(self, p):
        '''labeled_statement : label ':' statement'''
        p[0] = Node("LabelStmt", value=p[1], children=[p[3]])

    def p_labeled_statement_no_short_if(self, p):
        '''labeled_statement_no_short_if : label ':' statement_no_short_if'''
        p[0] = Node("LabelStmt", value=p[1], children=[p[3]])

    def p_label(self, p):
        '''label : NAME'''
        p[0] = p[1]

    def p_if_then_statement(self, p):
        '''if_then_statement : IF '(' expression ')' statement'''
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[3].type == "bool":
            p[0] = Node("IfStmt", children=[p[3],p[5]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[3].type, children=[p[3]])
            p[0] = Node("IfStmt", type="error", children=[p[3], p[5]])
            print("line {}: condition in if statment is not of type bool".format(p.lineno(2)))
            # print("line {}: there will be an implicit conversion form '{}' to 'int'".format(p.lineno(2), p[3].type))

    def p_if_then_else_statement(self, p):
        '''if_then_else_statement : IF '(' expression ')' statement_no_short_if ELSE statement'''
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[7].name == "":
            p[7].name = "NullStmt"
        if p[3].type == "bool":
            p[0] = Node("IfStmt", children=[p[3], p[5], p[7]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[3].type, children=[p[3]])
            p[0] = Node("IfStmt", type="error", children=[p[3], p[5], p[7]])
            print("line {}: condition in if statement is not of type bool".format(p.lineno(2)))
            # print("line {}: there will be an implicit conversion form '{}' to 'int'".format(p.lineno(2), p[3].type))

    def p_if_then_else_statement_no_short_if(self, p):
        '''if_then_else_statement_no_short_if : IF '(' expression ')' statement_no_short_if ELSE statement_no_short_if'''
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[7].name == "":
            p[7].name = "NullStmt"
        if p[3].type == "bool":
            p[0] = Node("IfStmt", children=[p[3], p[5], p[7]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[3].type, children=[p[3]])
            p[0] = Node("IfStmt", type="error", children=[p[3], p[5], p[7]])
            print("line {}: condition in if statement is not of type bool".format(p.lineno(2)))
            # print("line {}: there will be an implicit conversion form '{}' to 'int'".format(p.lineno(2), p[3].type))

    def p_while_statement(self, p):
        '''while_statement : WHILE '(' expression ')' statement'''
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[3].type == "bool":
            p[0] = Node("WhileStmt", children=[p[3],p[5]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[3].type, children=[p[3]])
            p[0] = Node("WhileStmt", type="error", children=[p[3], p[5]])
            print("line {}: condition in while statement is not of type bool".format(p.lineno(2)))
            # print("line {}: there will be an implicit conversion form '{}' to 'int'".format(p.lineno(2), p[3].type))

    def p_while_statement_no_short_if(self, p):
        '''while_statement_no_short_if : WHILE '(' expression ')' statement_no_short_if'''
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[3].type == "bool":
            p[0] = Node("WhileStmt", children=[p[3],p[5]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[3].type, children=[p[3]])
            p[0] = Node("WhileStmt", children=[tmp,p[5]])
            print("line {}: condition in while statement is not of type bool".format(p.lineno(2)))
            # print("line {}: there will be an implicit conversion form '{}' to 'int'".format(p.lineno(2), p[3].type))

    def p_for_statement(self, p):
        '''for_statement : FOR '(' for_init_opt ';' expression_opt ';' for_update_opt ')' statement'''
        if p[3].name == "":
            p[3].name = "NullStmt"
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[7].name == "":
            p[7].name = "NullStmt"
        if p[9].name == "":
            p[9].name = "NullStmt"
        if p[5].type == 'bool':
            p[0] = Node("ForStmt", children=[p[3], p[5], p[7], p[9]])
        else:
            p[0] = Node("ForStmt", type="error", children=[p[3], p[5], p[7], p[9]])
            print("line {}: condition in while statement is not of type bool".format(p.lineno(2)))
        if p[3].name == "Decls":
            for node in p[3].children:
                symbol_table.remove(node.value)

    def p_for_statement_no_short_if(self, p):
        '''for_statement_no_short_if : FOR '(' for_init_opt ';' expression_opt ';' for_update_opt ')' statement_no_short_if'''
        if p[3].name == "":
            p[3].name = "NullStmt"
        if p[5].name == "":
            p[5].name = "NullStmt"
        if p[7].name == "":
            p[7].name = "NullStmt"
        if p[9].name == "":
            p[9].name = "NullStmt"
        if p[5].type == 'bool':
            p[0] = Node("ForStmt", children=[p[3], p[5], p[7], p[9]])
        else:
            p[0] = Node("ForStmt", type="error", children=[p[3], p[5], p[7], p[9]])

    def p_for_init_opt(self, p):
        '''for_init_opt : for_init
                        | empty'''
        p[0] = p[1]

    def p_for_init(self, p):
        '''for_init : statement_expression_list
                    | local_variable_declaration'''
        p[0] = p[1]

    def p_statement_expression_list(self, p):
        '''statement_expression_list : statement_expression
                                     | statement_expression_list ',' statement_expression'''
        if len(p) == 2:
            p[0] = Node("StmtList", children=[p[1]])
        elif len(p) == 4:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_expression_opt(self, p):
        '''expression_opt : expression
                          | empty'''
        p[0] = p[1]
        if not p[1].type:
            p[0].type = 'void'

    def p_for_update_opt(self, p):
        '''for_update_opt : for_update
                          | empty'''
        p[0] = p[1]

    def p_for_update(self, p):
        '''for_update : statement_expression_list'''
        p[1].name = "ForUpdate"
        p[0] = p[1]

    def p_enhanced_for_statement(self, p):
        '''enhanced_for_statement : enhanced_for_statement_header statement'''
        p[0] = Node("EnhancedFor", children=p[1].children+[p[2]])
        symbol_table.end_scope()


    def p_enhanced_for_statement_no_short_if(self, p):
        '''enhanced_for_statement_no_short_if : enhanced_for_statement_header statement_no_short_if'''
        p[0] = Node("EnhancedFor", children=p[1].children+[p[2]], type=p[1].type)

    def p_enhanced_for_statement_header(self, p):
        '''enhanced_for_statement_header : enhanced_for_statement_header_init ':' expression ')' '''
        if p[1].type != p[3].type or p[1].dims != p[3].dims:
            p[1].type = "error"
            print("line {}: the type of iterator and array do not match".format(p.lineno(2)))
        p[1].children.append(p[3])
        p[0] = p[1]

    def p_enhanced_for_statement_header_init(self, p):
        '''enhanced_for_statement_header_init : FOR '(' type NAME dims_opt'''
        symbol_table.begin_scope()
        p[4] = Node("VarDecl", value=p[4], type=p[3].type, dims=p[5].dims)
        p[4].sym_entry = symbol_table.insert(p[4].value, {'value': p[4].value, 'type':p[4].type, 'dims':p[4].dims, 'arraylen': 0, 'modifiers':None})
        p[0] = Node("EnhancedForHead", children=[p[4]])

    def p_enhanced_for_statement_header_init2(self, p):
        '''enhanced_for_statement_header_init : FOR '(' modifiers type NAME dims_opt'''
        symbol_table.begin_scope()
        p[5] = Node("VarDecl", type=p[4].type, dims=p[6].dims, modifiers=p[3].modifiers)
        p[4].sym_entry = symbol_table.insert(p[4].value, {'value': p[4].value, 'type':p[4].type, 'dims':p[4].dims, 'modifiers':p[4].modifiers, 'arraylen':0})
        p[0] = Node("EnhancedForHead", children=[p[5]])

    def p_statement_no_short_if(self, p):
        '''statement_no_short_if : statement_without_trailing_substatement
                                 | labeled_statement_no_short_if
                                 | if_then_else_statement_no_short_if
                                 | while_statement_no_short_if
                                 | for_statement_no_short_if
                                 | enhanced_for_statement_no_short_if'''
        p[0] = p[1]

    def p_assert_statement(self, p):
        '''assert_statement : ASSERT expression ';'
                            | ASSERT expression ':' expression ';' '''
        if len(p) == 4:
            if p[2].type == "int" or p[2].type == "bool":
                p[0] = Node("AssertStmt", children=[p[2]])
            else:
                print("line {}: assert Statement has type mismatch".format(p.lineno(1)))
                p[0] = Node("AssertStmt", type="error", children=[p[2]])
        elif len(p) == 6:
            if (p[2].type == "int" or p[2].type == "bool") and p[4].type == "string":
                p[0] = Node("AssertStmt", children=[p[2],p[4]])
            else:
                p[0] = Node("AssertStmt", type="error", children=[p[2],p[4]])
                print("line {}: assert Statement has type mismatch".format(p.lineno(1)))

    def p_empty_statement(self, p):
        '''empty_statement : ';' '''
        p[0] = Node("NullStmt")

    def p_switch_statement(self, p):
        '''switch_statement : SWITCH '(' expression ')' switch_block'''
        p[0] = Node("SwitchStmt", children=[p[3]]+p[5].children)
        if p[3].type != "int" and p[3].type != "char" and p[3].type != "byte" and p[3].type != "string":
            print("line {}: the switch statement requires expression of type int, char, byte or string".format(p.lineno(1)))
            return
        for node in p[5].children:
            if node.name != "DefaultStmt" and p[3].type != node.type:
                print("line {}: expression '{}' is not of type '{}'".format(node.lineno, node.children[0].value, p[3].type))
                p[0].type = "error"
            for node1 in node.children:
                if node1.name == "CaseStmt" and p[3].type != node1.type:
                    print("line {}: expression '{}' is not of type '{}'".format(node1.lineno, node1.children[0].value, p[3].type))
                    p[0].type = "error"

    def p_switch_block(self, p):
        '''switch_block : '{' '}' '''
        p[0] = Node("NullSwitchBlock")

    def p_switch_block2(self, p):
        '''switch_block : '{' switch_block_statements '}' '''
        p[0] = p[2]

    def p_switch_block3(self, p):
        '''switch_block : '{' switch_labels '}' '''
        p[0] = p[2]

    def p_switch_block4(self, p):
        '''switch_block : '{' switch_block_statements switch_labels '}' '''
        p[2].children.append(p[3])
        p[0] = p[2]

    def p_switch_block_statements(self, p):
        '''switch_block_statements : switch_block_statement
                                   | switch_block_statements switch_block_statement'''
        if len(p) == 2:
            p[0] = Node("CompoundStmt", children=p[1].children)
        elif len(p) == 3:
            p[1].children.extend(p[2].children)
            p[0] = p[1]

    def p_switch_block_statement(self, p):
        '''switch_block_statement : switch_labels block_statements'''
        p[1].children[-1].children.append(p[2])
        p[0] = p[1]

    def p_switch_labels(self, p):
        '''switch_labels : switch_label
                         | switch_labels switch_label'''
        if len(p) == 2:
            p[0] = Node("CaseStmts", children=[p[1]], type=p[1].type, lineno=p[1].lineno)
        elif len(p) == 3:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_switch_label(self, p):
        '''switch_label : CASE constant_expression ':'
                        | DEFAULT ':' '''
        if len(p) == 4:
            p[0] = Node("CaseStmt", children=[p[2]] ,type=p[2].type, lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = Node("DefaultStmt")

    def p_constant_expression(self, p):
        '''constant_expression : expression'''
        p[0] = p[1]

    def p_do_statement(self, p):
        '''do_statement : DO statement WHILE '(' expression ')' ';' '''
        if p[5].type == "bool":
            p[0] = Node("DoWhileStmt", children=[p[2],p[5]])
        else:
            tmp = Node("ImplicitCastExpr", type=p[5].type, children=[p[5]])
            p[0] = Node("DoWhileStmt", type="error", children=[p[2], p[5]])
            print("line {}: condition in while statement is not of type bool".format(p.lineno(2)))

    def p_break_statement(self, p):
        '''break_statement : BREAK ';'
                           | BREAK NAME ';' '''
        if len(p) == 3:
            p[0] = Node("BreakStmt")
        elif len(p) == 4:
            p[0] = Node("BreakStmt", value=p[2])

    def p_continue_statement(self, p):
        '''continue_statement : CONTINUE ';'
                              | CONTINUE NAME ';' '''
        if len(p) == 3:
            p[0] = Node("ContinueStmt")
        elif len(p) == 4:
            p[0] = Node("ContinueStmt", value=p[2])

    def p_return_statement(self, p):
        '''return_statement : RETURN expression_opt ';' '''
        p[0] = Node("ReturnStmt", children=[p[2]])
        if p[2].type != symbol_table.get_method_return_type():
            print("line {}: the return statement returns expressions of type '{}' instead of '{}'".format(p.lineno(1), p[2].type, symbol_table.get_method_return_type()))

    def p_synchronized_statement(self, p):
        '''synchronized_statement : SYNCHRONIZED '(' expression ')' block'''
        p[0] = Node("SynStmt", children=[p[3],p[5]])

    def p_throw_statement(self, p):
        '''throw_statement : THROW expression ';' '''
        p[0] = Node("ThrowStmt", children=[p[2]])

    def p_try_statement(self, p):
        '''try_statement : TRY try_block catches
                         | TRY try_block catches_opt finally'''
        if len(p) == 4:
            p[0] = Node("TryStmt", children=[p[2],p[3]])
        elif len(p) == 5:
            p[0] = Node("TryStmt", children=[p[2],p[3],p[4]])

    def p_try_block(self, p):
        '''try_block : block'''
        p[0] = p[1]

    def p_catches(self, p):
        '''catches : catch_clause
                   | catches catch_clause'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_catches_opt(self, p):
        '''catches_opt : catches'''
        p[0] = p[1]

    def p_catches_opt2(self, p):
        '''catches_opt : empty'''
        p[0] = p[1]

    def p_catch_clause(self, p):
        '''catch_clause : CATCH '(' catch_formal_parameter ')' block'''
        p[0] = Node("Catch", children=[p[3], p[5]])

    def p_catch_formal_parameter(self, p):
        '''catch_formal_parameter : modifiers_opt catch_type variable_declarator_id'''
        p[0] = Node("Catch Parameters", children=[p[1], p[2], p[3]])

    def p_catch_type(self, p):
        '''catch_type : union_type'''
        p[0] = p[1]

    def p_union_type(self, p):
        '''union_type : type
                      | union_type '|' type'''
        if len(p) == 2:
            p[0] = Node("Union Type", children=[p[1]])
        elif len(p) == 4:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_try_statement_with_resources(self, p):
        '''try_statement_with_resources : TRY resource_specification try_block catches_opt
                                        | TRY resource_specification try_block catches_opt finally'''
        if len(p) == 5:
            p[0] = Node("Try", children=[p[2], p[3], p[4]])
        elif len(p) == 6:
            p[0] = Node("Try", children=[p[2], p[3], p[4], p[5]])

    def p_resource_specification(self, p):
        '''resource_specification : '(' resources semi_opt ')' '''
        p[0] = p[1]

    def p_semi_opt(self, p):
        '''semi_opt : ';'
                    | empty'''
        p[0] = p[1]

    def p_resources(self, p):
        '''resources : resource
                     | resources trailing_semicolon resource'''
        if len(p) == 2:
            p[0] = Node("ResourceList", children=[p[1]])
        elif len(p) == 4:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_trailing_semicolon(self, p):
        '''trailing_semicolon : ';' '''
        p[0] = Node("NullStmt")

    def p_resource(self, p):
        '''resource : type variable_declarator_id '=' variable_initializer'''
        if p[4].type == p[1].type:
            p[0] = Node("Resource", type=p[1].type, children=[p[2], p[4]])
        else:
            print("line {}: Type mismatch in TRY statement".format(p.lineno(3)))

    def p_resource2(self, p):
        '''resource : modifiers type variable_declarator_id '=' variable_initializer'''
        if p[4].type == p[1].type:
            p[0] = Node("Resource", type=p[2].type, modifiers=p[1].type, children=[p[3], p[5]])
        else:
            print("line {}: Type mismatch in TRY statement".format(p.lineno(4)))

    def p_finally(self, p):
        '''finally : FINALLY block'''
        p[0] = Node("Finally", type=p[1].type, children=[p[1]])

    def p_explicit_constructor_invocation(self, p):
        '''explicit_constructor_invocation : THIS '(' argument_list_opt ')' ';'
                                           | SUPER '(' argument_list_opt ')' ';' '''
        p[0] = Node("ConstInvoc", children=[p[3]])

    def p_explicit_constructor_invocation2(self, p):
        '''explicit_constructor_invocation : type_arguments SUPER '(' argument_list_opt ')' ';'
                                           | type_arguments THIS '(' argument_list_opt ')' ';' '''
        # TODO: Type arguments still not implemented, requires updates
        p[0] = Node("ConstrInvoc", children=[p[3]])

    def p_explicit_constructor_invocation3(self, p):
        '''explicit_constructor_invocation : primary '.' SUPER '(' argument_list_opt ')' ';'
                                           | name '.' SUPER '(' argument_list_opt ')' ';'
                                           | primary '.' THIS '(' argument_list_opt ')' ';'
                                           | name '.' THIS '(' argument_list_opt ')' ';' '''
        # TODO: Requires lookup
        p[2] = Node("MemberExpr", value=p[2]+p[3], children=[p[5]])
        p[0] = Node("ConstrInvoc", children=[p[1], p[2]])

    def p_explicit_constructor_invocation4(self, p):
        '''explicit_constructor_invocation : primary '.' type_arguments SUPER '(' argument_list_opt ')' ';'
                                           | name '.' type_arguments SUPER '(' argument_list_opt ')' ';'
                                           | primary '.' type_arguments THIS '(' argument_list_opt ')' ';'
                                           | name '.' type_arguments THIS '(' argument_list_opt ')' ';' '''
        # TODO: Requires type_arguments to be implemented and lookup
        p[0] = ptg.eight_child_node("explicit_constructor_invocation", p[1], tmp1, p[3], tmp2, tmp3, p[6], tmp4, tmp5)

    def p_class_instance_creation_expression(self, p):
        '''class_instance_creation_expression : NEW type_arguments class_type '(' argument_list_opt ')' class_body_opt'''
        # TODO: Requires type_arguments to be implemented
        p[0] = ptg.seven_child_node("class_instance_creation_expression", tmp1, p[2], p[3], tmp2, p[5], tmp3, p[7])

    def p_class_instance_creation_expression2(self, p):
        '''class_instance_creation_expression : NEW class_type '(' argument_list_opt ')' class_body_opt'''
        p[0] = Node("ClassInstantiation", type=p[2].type, children=[p[4], p[6]])

    def p_class_instance_creation_expression3(self, p):
        '''class_instance_creation_expression : primary '.' NEW type_arguments class_type '(' argument_list_opt ')' class_body_opt'''
        # TODO: Requires type_arguments to be implemented
        p[0] = ptg.eight_child_node("class_instance_creation_expression", p[1], tmp1, tmp2, p[4], p[5], tmp3, p[7], tmp4)

    def p_class_instance_creation_expression4(self, p):
        '''class_instance_creation_expression : primary '.' NEW class_type '(' argument_list_opt ')' class_body_opt'''
        p[2] = Node("MemberExpr", value=p[2]+p[3], children=[p[6], p[8]])
        p[0] = Node("ClassInstantiation", type=p[4].type, children=[p[1], p[2]])

    def p_class_instance_creation_expression5(self, p):
        '''class_instance_creation_expression : class_instance_creation_expression_name NEW class_type '(' argument_list_opt ')' class_body_opt'''
        p[2] = Node("MemberExpr", value='.'+p[3], children=[p[6], p[8]])
        p[0] = Node("ClassInstantiation", type=p[4].type, children=[p[1], p[2]])

    def p_class_instance_creation_expression6(self, p):
        '''class_instance_creation_expression : class_instance_creation_expression_name NEW type_arguments class_type '(' argument_list_opt ')' class_body_opt'''
        # TODO: Requires type_arguments to be implemented
        p[0] = ptg.eight_child_node("class_instance_creation_instance", p[1], tmp1, p[3], p[4], tmp2, p[6], tmp3, p[8])


    def p_class_instance_creation_expression_name(self, p):
        '''class_instance_creation_expression_name : name '.' '''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                p[1].type = "error"
        p[0] = p[1]

    def p_class_body_opt(self, p):
        '''class_body_opt : class_body
                          | empty'''
        p[0] = p[1]

    def p_field_access(self, p):
        '''field_access : primary '.' NAME'''
        p[3] = Node("MemberExpr", value=p[3])
        if p[1].type == "error":
            p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])

        elif p[1].value[0] != ".":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
                if symbol_table.lookup_class(p[1].type):
                    entry = symbol_table.lookup_method(p[1].type, p[3].value)
                else:
                    entry = None
                if entry:
                    p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type=entry['type'], children=[p[1]], modifiers=entry['modifiers'], arraylen=entry['arraylen'], dims=entry['dims'], sym_entry=entry)
                elif p[1].value == 'this':
                    entry = symbol_table.get_entry(p[3].value)
                    p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type=entry['type'], children=[p[1]], modifiers=entry['modifiers'], arraylen=entry['arraylen'], dims=entry['dims'], sym_entry=entry)
                else:
                    print("line {}: there is no field named '{}' for object of type '{}'".format(p.lineno(2), p[3].value, p[1].type))
                    p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])
        else:
            if symbol_table.lookup_class(p[1].type):
                entry = symbol_table.lookup_method(p[1].type, p[3].value)
            else:
                entry = None
            if entry:
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type=entry['type'], children=[p[1]], modifiers=entry['modifiers'], arraylen=entry['arraylen'], dims=entry['dims'], sym_entry=entry)
            else:
                print("line {}: there is no field named '{}' for object of type '{}'".format(p.lineno(2), p[3].value, p[1].type))
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])


    def p_field_access2(self, p):
        '''field_access : SUPER '.' NAME'''
        # TODO: Not implemented completely
        p[2] = Node("FieldAccess", value=p[1]+p[2]+p[3])

    def p_array_access(self, p):
        '''array_access : name '[' expression ']' '''
        if p[1].type == "":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                p[1].type = "error"
            if entry and symbol_table.get_entry_in_method(p[1].value) == None:
                this = Node("DeclsRefExpr", value="this", sym_entry=symbol_table.get_entry('this'))
                p[1] = Node("FieldAccessExpr", value='.' + p[1].value, type=p[1].type, children=[this], modifiers=p[1].modifiers, arraylen=p[1].arraylen, dims=p[1].dims, sym_entry=entry)
        if p[3].type != "int":
            print("line {}: the array index in not of type int".format(p.lineno(2)))
        if p[1].dims < 1:
            print("line {}: the variable '{}' is not a array".format(p.lineno(2), p[1].value))
            p[0] = Node("ArrayAccess", value=p[1].value, children=[p[1],p[3]], type="error", arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=0)
            return
        if p[1].dims == 1:
            p[0] = Node("ArrayAccess",value=p[1].value ,children=[p[1],p[3]], type=p[1].type, arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=0)
            if (p[0].arraylen and isinstance(p[3].value, int) and p[3].value >= p[0].arraylen[0]):
                print("line {}: the array index '{}' is out of range".format(p.lineno(2), p[3].value))
            return
        p[0] = Node("ArrayAccess",value=p[1].value, children=[p[1],p[3]], type=p[1].type, arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=p[1].dims-1)
        if (p[0].arraylen and p[3].value >= p[0].arraylen[-p[0].dims+1]):
            print("line {}: the array index '{}' is out of range".format(p.lineno(2), p[3].value))

    def p_array_access1(self, p):
        '''array_access : primary_no_new_array '[' expression ']' '''
        if p[3].type != "int":
            print("line {}: the array index in not of type int".format(p.lineno(2)))
        if p[1].dims < 1:
            print("line {}: the variable is indexed more than the dimension it has".format(p.lineno(2)))
            p[0] = Node("ArrayAccess", children=[p[1],p[3]], type="error", arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=0)
            return
        if p[1].dims == 1:
            p[0] = Node("ArrayAccess",value=p[1].value ,children=[p[1],p[3]], type=p[1].type, arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=0)
            if (p[0].arraylen and isinstance(p[3].value, int) and p[3].value >= p[0].arraylen[0]):
                print("line {}: the array index '{}' is out of range".format(p.lineno(2), p[3].value))
            return
        p[0] = Node("ArrayAccess", children=[p[1],p[3]], type=p[1].type, arraylen=p[1].arraylen, modifiers=p[1].modifiers, dims=p[1].dims-1)
        if (p[0].arraylen[0] and p[3].value >= p[0].arraylen[-p[0].dims+1]):
            print("line {}: the array index '{}' is out of range".format(p.lineno(2), p[3].value))

    def p_array_access2(self, p):
        '''array_access : array_creation_with_array_initializer '[' expression ']' '''
        p[1] = Node("ImplicitCastExpr", children=[p[1]])
        p[0] = Node("ArrayAccess", type=p[1].type, children=[p[1], p[3]], modifiers=p[1].modifiers, dims=p[1].dims, arraylen=p[1].arraylen)

    def p_array_creation_with_array_initializer(self, p):
        '''array_creation_with_array_initializer : NEW primitive_type dim_with_or_without_exprs array_initializer
                                                 | NEW class_or_interface_type dim_with_or_without_exprs array_initializer'''
        p[0] = Node("ArrayInitialization", type=p[2].type, children=[p[3], p[4]], dims=p[3].dims, arraylen=p[3].arraylen)

    def p_dim_with_or_without_exprs(self, p):
        '''dim_with_or_without_exprs : dim_with_or_without_expr
                                     | dim_with_or_without_exprs dim_with_or_without_expr'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[1].dims += 1
            p[1].arraylen.extend(p[2].arraylen)
            p[0] = p[1]

    def p_dim_with_or_without_expr(self, p):
        '''dim_with_or_without_expr : '[' expression ']'
                                    | '[' ']' '''
        if len(p) == 3:
            p[1] = Node(dims=1, arraylen=0)
        elif len(p) == 4:
            p[2].dims = 1
            p[2].arraylen = [p[2].value]
            p[0] = p[2]

    def p_array_creation_without_array_initializer(self, p):
        '''array_creation_without_array_initializer : NEW primitive_type dim_with_or_without_exprs
                                                    | NEW class_or_interface_type dim_with_or_without_exprs'''
        p[0] = Node("ArrayInitialization", type=p[2].type, children=[p[3]], dims=p[3].dims, arraylen=p[3].arraylen)

class NameParser(object):

    def p_name(self, p):
        '''name : simple_name
                | qualified_name'''
        p[0] = p[1]

    def p_simple_name(self, p):
        '''simple_name : NAME'''
        p[0] = Node("DeclsRefExpr", value=p[1], lineno=p.lineno(1))

    def p_qualified_name(self, p):
        '''qualified_name : name '.' simple_name'''
        if p[1].type == "error":
            p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])

        elif p[1].value[0] != ".":
            entry = symbol_table.get_entry(p[1].value)
            if entry:
                p[1].type = entry['type']
                p[1].dims = entry['dims']
                p[1].arraylen = entry['arraylen']
                p[1].modifiers = entry['modifiers']
                p[1].sym_entry = entry
                if symbol_table.lookup_class(p[1].type):
                    entry = symbol_table.lookup_method(p[1].type, p[3].value)
                else:
                    entry = None
                if entry:
                    p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type=entry['type'], children=[p[1]], modifiers=entry['modifiers'], arraylen=entry['arraylen'], dims=entry['dims'], sym_entry=entry)
                else:
                    print("line {}: there is no field named '{}' for object of type '{}'".format(p.lineno(2), p[3].value, p[1].type))
                    p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])
            else:
                print("line {}: the variable '{}' is undeclared".format(p.lineno(2), p[1].value))
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])
        else:
            if symbol_table.lookup_class(p[1].type):
                entry = symbol_table.lookup_method(p[1].type, p[3].value)
            else:
                entry = None
            if entry:
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type=entry['type'], children=[p[1]], modifiers=entry['modifiers'], arraylen=entry['arraylen'], dims=entry['dims'], sym_entry=entry)
            else:
                print("line {}: there is no field named '{}' for object of type '{}'".format(p.lineno(2), p[3].value, p[1].type))
                p[0] = Node("FieldAccessExpr", value=p[2] + p[3].value, type="error", children=[p[1]])

class LiteralParser(object):

    def p_literal1(self, p):
        '''literal : NUM'''
        value = literal_eval(p[1])
        if isinstance(value, int):
            p[0] = Node("IntegerLiteral", value=value, type="int")
        if isinstance(value, float):
            p[0] = Node("FloatLiteral", value=value, type="float")

    def p_literal2(self, p):
        '''literal : CHAR_LITERAL'''
        p[0] = Node("CharLiteral", value=p[1], type="char")

    def p_literal3(self, p):
        '''literal : STRING_LITERAL'''
        p[0] = Node("StringLiteral", value=p[1], type="string")

    def p_literal4(self, p):
        '''literal : TRUE
                   | FALSE'''
        p[0] = Node("Boolean", value=p[1], type="bool")

    def p_literal5(self, p):
        '''literal : NULL'''
        p[0] = Node("Null", value=p[1], type="null")

class TypeParser(object):

    def p_modifiers_opt(self, p):
        '''modifiers_opt : modifiers'''
        p[0] = p[1]

    def p_modifiers_opt2(self, p):
        '''modifiers_opt : empty'''
        p[0] = p[1]

    def p_modifiers(self, p):
        '''modifiers : modifier
                     | modifiers modifier'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[1].modifiers.extend(p[2].modifiers)
            p[0] = p[1]

    def p_modifier(self, p):
        '''modifier : PUBLIC
                    | PROTECTED
                    | PRIVATE
                    | STATIC
                    | ABSTRACT
                    | FINAL
                    | NATIVE
                    | SYNCHRONIZED
                    | TRANSIENT
                    | VOLATILE
                    | STRICTFP'''
        p[0] = Node("Modifier", modifiers=[p[1]])

    def p_modifier2(self, p):
        '''modifier : annotation'''
        p[0] = p[1]

    def p_type(self, p):
        '''type : primitive_type
                | reference_type'''
        p[0] = p[1]

    def p_primitive_type(self, p):
        '''primitive_type : BOOLEAN
                          | VOID
                          | BYTE
                          | SHORT
                          | INT
                          | LONG
                          | CHAR
                          | FLOAT
                          | DOUBLE'''
        p[0] = Node("Type", type=p[1])

    def p_reference_type(self, p):
        '''reference_type : class_or_interface_type
                          | array_type'''
        p[0] = p[1]

    def p_class_or_interface_type(self, p):
        '''class_or_interface_type : class_or_interface
                                   | generic_type'''
        p[0] = p[1]

    def p_class_type(self, p):
        '''class_type : class_or_interface_type'''
        p[0] = p[1]

    def p_class_or_interface(self, p):
        '''class_or_interface : name
                              | generic_type '.' name'''
        if len(p) == 2:
            if symbol_table.lookup_class(p[1].value) == False:
                print("line {}: Object '{}' not defined".format(p[1].lineno, p[1].value))
            p[1].type = p[1].value
            p[0] = p[1]
        elif len(p) == 4:
            p[1].type = p[1].type + '.' + p[3].value
            p[0] = p[1]

    def p_generic_type(self, p):
        '''generic_type : class_or_interface type_arguments'''
        p[1].type = p[1].type + p[2].type
        p[0] = p[1]

    def p_generic_type2(self, p):
        '''generic_type : class_or_interface '<' '>' '''
        p[1].type = p[1].type + '< >'
        p[0] = p[1]

    def p_array_type(self, p):
        '''array_type : primitive_type dims
                      | generic_type dims'''
        p[1].dims = p[2].dims
        p[0] = p[1]

    def p_array_type2(self, p):
        '''array_type : name dims'''
        if symbol_table.lookup_class(p[1].value) == False:
            print("line {}: Object '{}' not defined".format(p[1].lineno, p[1].value))
        p[1].type = p[1].value
        p[1].dims = p[2].dims
        p[0] = p[1]

    def p_array_type3(self, p):
        '''array_type : generic_type '.' name dims'''
        # TODO: Requires lookup
        p[1].type = p[1].type + '.' + p[3].value + p[4].type
        p[0] = p[1]

    def p_type_arguments(self, p):
        '''type_arguments : '<' type_argument_list1'''
        p[0] = p[1]

    def p_type_argument_list1(self, p):
        '''type_argument_list1 : type_argument1
                               | type_argument_list ',' type_argument1'''
        if len(p) == 2:
            p[0] = Node()
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_argument_list1",  p[1], tmp, p[3])

    def p_type_argument_list(self, p):
        '''type_argument_list : type_argument
                              | type_argument_list ',' type_argument'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_argument_list", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_argument_list",  p[1], tmp, p[3])

    def p_type_argument(self, p):
        '''type_argument : reference_type
                         | wildcard'''
        p[0] = ptg.one_child_node("type_argument", p[1])

    def p_type_argument1(self, p):
        '''type_argument1 : reference_type1
                          | wildcard1'''
        p[0] = ptg.one_child_node("type_argument1", p[1])

    def p_reference_type1(self, p):
        '''reference_type1 : reference_type '>'
                           | class_or_interface '<' type_argument_list2'''
        if len(p) == 3:
            tmp = ptg.node_create(">")
            p[0] = ptg.two_child_node("reference_type1", p[1], tmp)
        else:
            tmp = ptg.node_create("<")
            p[0] = ptg.three_child_node("reference_type1",  p[1], tmp, p[3])

    def p_type_argument_list2(self, p):
        '''type_argument_list2 : type_argument2
                               | type_argument_list ',' type_argument2'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_argument_list2", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_argument_list2",  p[1], tmp, p[3])

    def p_type_argument2(self, p):
        '''type_argument2 : reference_type2
                          | wildcard2'''
        p[0] = ptg.one_child_node("type_argument2", p[1])

    def p_reference_type2(self, p):
        '''reference_type2 : reference_type RSHIFT
                           | class_or_interface '<' type_argument_list3'''
        if len(p) == 3:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.two_child_node("reference_type2", p[1], tmp)
        else:
            tmp = ptg.node_create("<")
            p[0] = ptg.three_child_node("reference_type2",  p[1], tmp, p[3])

    def p_type_argument_list3(self, p):
        '''type_argument_list3 : type_argument3
                               | type_argument_list ',' type_argument3'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_argument_list3", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_argument_list3",  p[1], tmp, p[3])

    def p_type_argument3(self, p):
        '''type_argument3 : reference_type3
                          | wildcard3'''
        p[0] = ptg.one_child_node("type_argument3", p[1])

    def p_reference_type3(self, p):
        '''reference_type3 : reference_type RRSHIFT'''
        tmp = ptg.node_create(p[2])
        p[0] = ptg.two_child_node("reference_type3", p[1], tmp)

    def p_wildcard(self, p):
        '''wildcard : '?'
                    | '?' wildcard_bounds'''
        if len(p) == 2:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.one_child_node("wildcard", tmp)
        else:
            tmp = ptg.node_create("?")
            p[0] = ptg.three_child_node("wildcard", tmp, p[2])

    def p_wildcard_bounds(self, p):
        '''wildcard_bounds : EXTENDS reference_type
                           | SUPER reference_type'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("wildcard_bounds", tmp, p[2])

    def p_wildcard1(self, p):
        '''wildcard1 : '?' '>'
                     | '?' wildcard_bounds1'''
        if p[2] == '>':
            tmp1 = ptg.node_create(p[1])
            tmp2 = ptg.node_create(p[2])
            p[0] = ptg.one_child_node("wildcard1", tmp1, tmp2)
        else:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.one_child_node("wildcard1", tmp, p[2])

    def p_wildcard_bounds1(self, p):
        '''wildcard_bounds1 : EXTENDS reference_type1
                            | SUPER reference_type1'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("wildcard_bounds1", tmp, p[2])

    def p_wildcard2(self, p):
        '''wildcard2 : '?' RSHIFT
                     | '?' wildcard_bounds2'''
        if p[2] == '>>':
            tmp1 = ptg.node_create(p[1])
            tmp2 = ptg.node_create(p[2])
            p[0] = ptg.one_child_node("wildcard2", tmp1, tmp2)
        else:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.one_child_node("wildcard2", tmp, p[2])

    def p_wildcard_bounds2(self, p):
        '''wildcard_bounds2 : EXTENDS reference_type2
                            | SUPER reference_type2'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("wildcard_bounds2", tmp, p[2])

    def p_wildcard3(self, p):
        '''wildcard3 : '?' RRSHIFT
                     | '?' wildcard_bounds3'''
        if p[2] == '>>>':
            tmp1 = ptg.node_create(p[1])
            tmp2 = ptg.node_create(p[2])
            p[0] = ptg.one_child_node("wildcard3", tmp1, tmp2)
        else:
            tmp = ptg.node_create(p[1])
            p[0] = ptg.one_child_node("wildcard3", tmp, p[2])

    def p_wildcard_bounds3(self, p):
        '''wildcard_bounds3 : EXTENDS reference_type3
                            | SUPER reference_type3'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("wildcard_bounds3", tmp, p[2])

    def p_type_parameter_header(self, p):
        '''type_parameter_header : NAME'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.one_child_node("type_parameter_header", tmp)

    def p_type_parameters(self, p):
        '''type_parameters : '<' type_parameter_list1'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("type_parameters", tmp, p[2])

    def p_type_parameter_list(self, p):
        '''type_parameter_list : type_parameter
                               | type_parameter_list ',' type_parameter'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_parameter_list", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_parameter_list",  p[1], tmp, p[3])

    def p_type_parameter(self, p):
        '''type_parameter : type_parameter_header
                          | type_parameter_header EXTENDS reference_type
                          | type_parameter_header EXTENDS reference_type additional_bound_list'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_parameter", p[1])
        elif len(p) == 4:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("type_parameter",  p[1], tmp, p[3])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.four_child_node("type_parameter",  p[1], tmp, p[3], p[4])

    def p_additional_bound_list(self, p):
        '''additional_bound_list : additional_bound
                                 | additional_bound_list additional_bound'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("additional_bound_list", p[1])
        else:
            p[0] = ptg.two_child_node("additional_bound_list", p[1], p[2])

    def p_additional_bound(self, p):
        '''additional_bound : '&' reference_type'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("additional_bound",  tmp, p[2])

    def p_type_parameter_list1(self, p):
        '''type_parameter_list1 : type_parameter1
                                | type_parameter_list ',' type_parameter1'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("type_parameter_list1", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("type_parameter_list1",  p[1], tmp, p[3])

    def p_type_parameter1(self, p):
        '''type_parameter1 : type_parameter_header '>'
                           | type_parameter_header EXTENDS reference_type1
                           | type_parameter_header EXTENDS reference_type additional_bound_list1'''
        if len(p) == 3:
            tmp = ptg.node_create(">")
            p[0] = ptg.two_child_node("type_parameter1", p[1], tmp)
        elif len(p) == 4:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.three_child_node("type_parameter1",  p[1], tmp, p[3])
        else:
            tmp = ptg.node_create(p[2])
            p[0] = ptg.four_child_node("type_parameter1",  p[1], tmp, p[3], p[4])

    def p_additional_bound_list1(self, p):
        '''additional_bound_list1 : additional_bound1
                                  | additional_bound_list additional_bound1'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("additional_bound_list1", p[1])
        else:
            p[0] = ptg.two_child_node("additional_bound_list1", p[1], p[2])

    def p_additional_bound1(self, p):
        '''additional_bound1 : '&' reference_type1'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("additional_bound1",  tmp, p[2])

class ClassParser(object):

    def p_type_declaration(self, p):
        '''type_declaration : class_declaration
                            | interface_declaration
                            | enum_declaration
                            | annotation_type_declaration'''
        p[0] = p[1]

    def p_type_declaration2(self, p):
        '''type_declaration : ';' '''
        p[0] = Node("NullStmt")

    def p_class_declaration(self, p):
        '''class_declaration : class_header class_body'''
        symbol_table.insert_class(p[1].children[0].value)
        symbol_table.end_scope()
        p[0] = Node("ClassDecl", type=p[2].type, children=[p[1],p[2]])

    def p_class_header(self, p):
        '''class_header : class_header_name class_header_extends_opt class_header_implements_opt'''
        p[0] = Node("ClassHeader", children=[p[1], p[2], p[3]])

    def p_class_header_name(self, p):
        '''class_header_name : class_header_name1 type_parameters
                             | class_header_name1'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # TODO:Not done!!!!!
             p[0] = p[1]

    def p_class_header_name1(self, p):
        '''class_header_name1 : modifiers_opt CLASS NAME'''
        symbol_table.begin_scope(name=p[3], category=p[2])
        p[0] = Node("ClassName", value=p[3], modifiers=p[1].modifiers)

    def p_class_header_extends_opt(self, p):
        '''class_header_extends_opt : class_header_extends
                                    | empty'''
        p[0] = p[1]

    def p_class_header_extends(self, p):
        '''class_header_extends : EXTENDS class_type'''
        p[0] = Node("ClassExtends", type=p[2].type)

    def p_class_header_implements_opt(self, p):
        '''class_header_implements_opt : class_header_implements
                                       | empty'''
        p[0] = p[1]

    def p_class_header_implements(self, p):
        '''class_header_implements : IMPLEMENTS interface_type_list'''
        p[2].name = "ClassImplements"
        p[0] = p[2]

    def p_interface_type_list(self, p):
        '''interface_type_list : interface_type
                               | interface_type_list ',' interface_type'''
        if len(p) == 2:
            p[0] = Node("InterfaceTypes", children=[p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_interface_type(self, p):
        '''interface_type : class_or_interface_type'''
        p[0] = p[1]

    def p_class_body(self, p):
        '''class_body : '{' class_body_declarations_opt '}' '''
        p[0] = p[2]

    def p_class_body_declarations_opt(self, p):
        '''class_body_declarations_opt : class_body_declarations'''
        p[0] = p[1]

    def p_class_body_declarations_opt2(self, p):
        '''class_body_declarations_opt : empty'''
        p[0] = p[1]

    def p_class_body_declarations(self, p):
        '''class_body_declarations : class_body_declaration
                                   | class_body_declarations class_body_declaration'''
        if len(p) == 2:
            p[0] = Node("ClassBodyDecls", type=p[1].type, children=[p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
            if p[1].type == "error" or p[2].type == "error":
                p[0].type = "error"

    def p_class_body_declaration(self, p):
        '''class_body_declaration : class_member_declaration
                                  | static_initializer
                                  | constructor_declaration'''
        p[0] = p[1]

    def p_class_body_declaration2(self, p):
        '''class_body_declaration : block'''
        p[0] = p[1]

    def p_class_member_declaration(self, p):
        '''class_member_declaration : field_declaration
                                    | class_declaration
                                    | method_declaration
                                    | interface_declaration
                                    | enum_declaration
                                    | annotation_type_declaration'''
        p[0] = p[1]

    def p_class_member_declaration2(self, p):
        '''class_member_declaration : ';' '''
        p[0] = Node("NullStmt")

    def p_field_declaration(self, p):
        '''field_declaration : modifiers_opt type variable_declarators ';' '''
        for node in p[3].children:
            if (node.type != "") and (node.type == "" or node.type != p[2].type):
                print("line {}: variable '{}' (type '{}') initialized to type '{}'".format(node.lineno, node.value, p[2].type, node.type))
                p[3].type = "error"
            node.type = p[2].type
            if node.dims == 0:
                node.dims = p[2].dims
            node.modifiers = p[1].modifiers
            if symbol_table.get_entry(node.value):
                print("line {}: variable '{}' is already declared".format(node.lineno, node.value))
            else:
                node.sym_entry = symbol_table.insert(node.value, {'value': node.value, 'type':node.type, 'modifiers':node.modifiers, 'dims':node.dims, 'arraylen':node.arraylen})
        p[3].name = "FieldDecl"
        p[0] = p[3]

    def p_static_initializer(self, p):
        '''static_initializer : STATIC block'''
        p[2].name = "StaticBlock"
        p[0] = p[2]

    def p_constructor_declaration(self, p):
        '''constructor_declaration : constructor_header method_body'''
        symbol_table.print_table("csv/" + p[1].children[0].value + "_constructor.csv")
        symbol_table.end_scope()
        p[0] = Node("ConstrDecl", children=[p[1], p[2]])

    def p_constructor_header(self, p):
        '''constructor_header : constructor_header_name formal_parameter_list_opt ')' method_header_throws_clause_opt'''
        # TODO: Not done because of nayan
        p[0] = Node("ConstructorHeader", children=[p[1], p[2], p[4]])

    def p_constructor_header_name(self, p):
        '''constructor_header_name : modifiers_opt type_parameters NAME '('
                                   | modifiers_opt NAME '(' '''
        if len(p) == 4:
            if symbol_table.get_name() != (p[2], "class"):
                print("lineno {}: Illegal declaration, {} (constructor or method) in class {}".format(p.lineno(2), p[2], symbol_table.table.name))
            symbol_table.begin_scope(name=p[2], category="constructor")
            p[0] = Node("DeclsRefExpr", value=p[2], modifiers=p[1].modifiers)
        else:
            # TODO: type_parameters has to be implemented
            p[0] = ptg.four_child_node("constructor_header_name", p[1], p[2], tmp, lparen)

    def p_formal_parameter_list_opt(self, p):
        '''formal_parameter_list_opt : formal_parameter_list'''
        p[0] = p[1]
        symbol_table.args_completed()

    def p_formal_parameter_list_opt2(self, p):
        '''formal_parameter_list_opt : empty'''
        p[0] = p[1]
        symbol_table.args_completed()

    def p_formal_parameter_list(self, p):
        '''formal_parameter_list : formal_parameter
                                 | formal_parameter_list ',' formal_parameter'''
        if len(p) == 2:
            p[0] = Node("MethodParameters", children=[p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_formal_parameter(self, p):
        '''formal_parameter : modifiers_opt type variable_declarator_id
                            | modifiers_opt type ELLIPSIS variable_declarator_id'''
        if len(p) == 4:
            p[3].type = p[2].type
            p[3].dims = p[2].dims
            p[3].modifiers = p[1].modifiers
            entry = symbol_table.get_entry(p[3].value)
            if entry:
                print("line {}: variable '{}' is already declared".format(p[3].lineno, p[3].value))
            else:
                p[3].sym_entry = symbol_table.insert(p[3].value, {'value': p[3].value, 'type':p[3].type, 'dims':p[3].dims, 'arraylen':p[3].arraylen, 'modifiers':p[3].modifiers})
                p[3].sym_entry['offset'] += 8
            p[0] = p[3]
        else:
            p[4].type = p[2].type
            p[4].modifiers = p[1].modifiers
            entry = symbol_table.get_entry(p[4].value)
            if entry:
                print("line {}: variable '{}' is already declared".format(p[4].lineno, p[4].value))
            else:
                p[4].sym_entry = symbol_table.insert(p[4].value, {'value': p[4].value, 'type':p[4].type, 'dims':p[4].dims, 'arraylen':p[4].arraylen, 'modifiers':p[4].modifiers})
                p[4].sym_entry['offset'] += 8
            p[0] = p[4]

    def p_method_header_throws_clause_opt(self, p):
        '''method_header_throws_clause_opt : method_header_throws_clause
                                           | empty'''
        p[0] = p[1]

    def p_method_header_throws_clause(self, p):
        '''method_header_throws_clause : THROWS class_type_list'''
        p[2].name = "Throws"
        p[0] = p[2]

    def p_class_type_list(self, p):
        '''class_type_list : class_type_elt
                           | class_type_list ',' class_type_elt'''
        if len(p) == 2:
            p[0] = Node("ThrowsList", children=[p[1]])
        else:
            p[3].children.append(p[1])

    def p_class_type_elt(self, p):
        '''class_type_elt : class_type'''
        p[0] = p[1]

    def p_method_body(self, p):
        '''method_body : '{' block_statements_opt '}' '''
        p[2].name = "MethodBody"
        p[2].lineno = p.lineno(3)
        p[0] = p[2]

    def p_method_declaration(self, p):
        '''method_declaration : abstract_method_declaration
                              | method_header method_body'''
        if len(p) == 2:
            symbol_table.end_scope()
            p[0] = p[1]
        else:
            if p[2].value == "" and p[1].type.split(" ", 1)[0] != "void":
                print("line {}: control reaches end of non-void function '{}'".format(p[2].lineno, p[1].children[0].value))
            if p[2].value == "" and p[1].type.split(" ", 1)[0] == "void":
                p[2].children += [Node("ReturnStmt", children=[Node()])]
            symbol_table.print_table("csv/" + symbol_table.get_class_name() + "_" + p[1].children[0].value + "_method.csv")
            symbol_table.end_scope()
            p[0] = Node("MethodDecl", children=[p[1],p[2]])
            if p[1].type == "error" or p[2].type == "error":
                p[0].type = "error"

    def p_abstract_method_declaration(self, p):
        '''abstract_method_declaration : method_header ';' '''
        p[0] = p[1]

    def p_method_header(self, p):
        '''method_header : method_header_name formal_parameter_list_opt ')' method_header_extended_dims method_header_throws_clause_opt'''
        if p[4].name == "" and p[5].name == "":
            p[0] = Node("MethodHeader", children=[p[1], p[2]])
        elif p[4].name == "" and p[5].name != "":
            p[0] = Node("MethodHeader", children=[p[1], p[2], p[5]])
        elif p[4].name != "" and p[5].name == "":
            p[0] = Node("MethodHeader", children=[p[1], p[2], p[4]])
        p[0].type = p[1].type + " ("
        length = len(p[2].children)
        if length == 0:
            p[0].type += "int"
        else:
            p[0].type += "int,"
        for node in p[2].children:
            if node == p[2].children[length - 1]:
                p[0].type += node.type
            else:
                p[0].type += node.type + ","
        p[0].type += ")"
        p[0].sym_entry = symbol_table.insert_up(p[1].value, {'value': p[1].value, 'type':p[0].type, 'modifiers': p[1].modifiers})

    def p_method_header_name(self, p):
        '''method_header_name : modifiers_opt type_parameters type NAME '('
                              | modifiers_opt type NAME '(' '''
        if len(p) == 5:
            symbol_table.begin_scope(name=p[3], category="method")
            entry = symbol_table.insert('this', {'value': 'this', 'type':'int', 'dims':0, 'arraylen':[], 'modifiers':[]})
            entry['offset'] += 8
            p[0] = Node("MethodName", value=p[3], type=p[2].type, modifiers=p[1].modifiers)
        else:
            #TODO:Not done because of type_parameters
            p[0] = Node("MethodName", value=p[4], type=p[2].type, modifiers=p[1].modifiers)

    def p_method_header_extended_dims(self, p):
        '''method_header_extended_dims : dims_opt'''
        p[0] = p[1]

    def p_interface_declaration(self, p):
        '''interface_declaration : interface_header interface_body'''

    def p_interface_header(self, p):
        '''interface_header : interface_header_name interface_header_extends_opt'''
        p[0] = ptg.two_child_node("interface_header", p[1], p[2])

    def p_interface_header_name(self, p):
        '''interface_header_name : interface_header_name1 type_parameters
                                 | interface_header_name1'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("interface_header_name", p[1])
        else:
            p[0] = ptg.two_child_node("interface_header_name", p[1], p[2])

    def p_interface_header_name1(self, p):
        '''interface_header_name1 : modifiers_opt INTERFACE NAME'''
        tmp1 = ptg.node_create(p[2])
        tmp2 = ptg.node_create(p[3])
        p[0] = ptg.three_child_node("interface_header_name1", p[1], tmp1, tmp2)

    def p_interface_header_extends_opt(self, p):
        '''interface_header_extends_opt : interface_header_extends'''
        p[0] = ptg.one_child_node("interface_header_extends_opt", p[1])

    def p_interface_header_extends_opt2(self, p):
        '''interface_header_extends_opt : empty'''
        p[0] = ptg.one_child_node("interface_header_extends_opt", p[1])

    def p_interface_header_extends(self, p):
        '''interface_header_extends : EXTENDS interface_type_list'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("interface_header_extends", tmp, p[2])

    def p_interface_body(self, p):
        '''interface_body : '{' interface_member_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        p[0] = ptg.three_child_node("interface_body", lbrace, p[2], rbrace)

    def p_interface_member_declarations_opt(self, p):
        '''interface_member_declarations_opt : interface_member_declarations'''
        p[0] = ptg.one_child_node("interface_member_declarations_opt", p[1])

    def p_interface_member_declarations_opt2(self, p):
        '''interface_member_declarations_opt : empty'''
        p[0] = ptg.one_child_node("interface_member_declarations_opt", p[1])

    def p_interface_member_declarations(self, p):
        '''interface_member_declarations : interface_member_declaration
                                         | interface_member_declarations interface_member_declaration'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("interface_member_declarations", p[1])
        else:
            p[0] = ptg.two_child_node("interface_member_declarations", p[1], p[2])

    def p_interface_member_declaration(self, p):
        '''interface_member_declaration : constant_declaration
                                        | abstract_method_declaration
                                        | class_declaration
                                        | interface_declaration
                                        | enum_declaration
                                        | annotation_type_declaration'''
        p[0] = ptg.one_child_node("interface_member_declaration", p[1])

    def p_interface_member_declaration2(self, p):
        '''interface_member_declaration : ';' '''
        tmp = ptg.node_create(";")
        p[0] = ptg.one_child_node("interface_member_declaration", tmp)

    def p_constant_declaration(self, p):
        '''constant_declaration : field_declaration'''
        p[0] = ptg.one_child_node("constant_declaration", p[1])

    def p_enum_declaration(self, p):
        '''enum_declaration : enum_header enum_body'''
        p[0] = ptg.two_child_node("enum_declaration", p[1], p[2])

    def p_enum_header(self, p):
        '''enum_header : enum_header_name class_header_implements_opt'''
        p[0] = ptg.two_child_node("enum_header", p[1], p[2])

    def p_enum_header_name(self, p):
        '''enum_header_name : modifiers_opt ENUM NAME
                            | modifiers_opt ENUM NAME type_parameters'''
        if len(p) == 4:
            tmp1 = ptg.node_create(p[2])
            tmp2 = ptg.node_create(p[3])
            p[0] = ptg.three_child_node("enum_header_name", p[1], tmp1, tmp2)
        else:
            tmp1 = ptg.node_create(p[2])
            tmp2 = ptg.node_create(p[3])
            p[0] = ptg.four_child_node("enum_header_name", p[1], tmp1, tmp2, p[4])

    def p_enum_body(self, p):
        '''enum_body : '{' enum_body_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        p[0] = ptg.three_child_node("enum_body", lbrace, p[2], rbrace)

    def p_enum_body2(self, p):
        '''enum_body : '{' ',' enum_body_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        tmp = ptg.node_create("\,")
        p[0] = ptg.four_child_node("enum_body", lbrace, tmp, p[3], rbrace)

    def p_enum_body3(self, p):
        '''enum_body : '{' enum_constants ',' enum_body_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        tmp = ptg.node_create("\,")
        p[0] = ptg.five_child_node("enum_body", lbrace, p[2], tmp, p[4], rbrace)

    def p_enum_body4(self, p):
        '''enum_body : '{' enum_constants enum_body_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        p[0] = ptg.four_child_node("enum_body", lbrace, p[2], p[3], rbrace)

    def p_enum_constants(self, p):
        '''enum_constants : enum_constant
                          | enum_constants ',' enum_constant'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("enum_constants", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("enum_constants",  p[1], tmp, p[3])

    def p_enum_constant(self, p):
        '''enum_constant : enum_constant_header class_body
                         | enum_constant_header'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("enum_constant", p[1])
        else:
            p[0] = ptg.two_child_node("enum_constant", p[1], p[2])

    def p_enum_constant_header(self, p):
        '''enum_constant_header : enum_constant_header_name arguments_opt'''
        p[0] = ptg.two_child_node("enum_constant_header", p[1], p[2])

    def p_enum_constant_header_name(self, p):
        '''enum_constant_header_name : modifiers_opt NAME'''
        tmp = ptg.node_create(p[2])
        p[0] = ptg.two_child_node("enum_constant_header_name", p[1], tmp)

    def p_arguments_opt(self, p):
        '''arguments_opt : arguments'''
        p[0] = ptg.one_child_node("arguments_opt", p[1])

    def p_arguments_opt2(self, p):
        '''arguments_opt : empty'''
        p[0] = ptg.one_child_node("arguments_opt", p[1])

    def p_arguments(self, p):
        '''arguments : '(' argument_list_opt ')' '''
        lparen = ptg.node_create("(")
        rparen = ptg.node_create(")")
        p[0] = ptg.three_child_node("arguments", lparen, p[2], rparen)

    def p_argument_list_opt(self, p):
        '''argument_list_opt : argument_list'''
        p[0] = p[1]

    def p_argument_list_opt2(self, p):
        '''argument_list_opt : empty'''
        p[0] = p[1]

    def p_argument_list(self, p):
        '''argument_list : expression
                         | argument_list ',' expression'''
        if len(p) == 2:
            p[0] = Node("ArgumentList", children=[p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_enum_body_declarations_opt(self, p):
        '''enum_body_declarations_opt : enum_declarations'''
        p[0] = ptg.one_child_node("enum_body_declarations_opt", p[1])

    def p_enum_body_declarations_opt2(self, p):
        '''enum_body_declarations_opt : empty'''
        p[0] = ptg.one_child_node("enum_body_declarations_opt", p[1])

    def p_enum_body_declarations(self, p):
        '''enum_declarations : ';' class_body_declarations_opt'''
        tmp = ptg.node_create(";")
        p[0] = ptg.two_child_node("enum_declarations", tmp, p[2])

    def p_annotation_type_declaration(self, p):
        '''annotation_type_declaration : annotation_type_declaration_header annotation_type_body'''
        p[0] = ptg.two_child_node("annotation_type_declaration", p[1], p[2])

    def p_annotation_type_declaration_header(self, p):
        '''annotation_type_declaration_header : annotation_type_declaration_header_name class_header_extends_opt class_header_implements_opt'''
        p[0] = ptg.three_child_node("annotation_type_declaration_header", p[1], p[2], p[3])

    def p_annotation_type_declaration_header_name(self, p):
        '''annotation_type_declaration_header_name : modifiers '@' INTERFACE NAME'''
        tmp1 = ptg.node_create("@")
        tmp2 = ptg.node_create(p[3])
        tmp3 = ptg.node_create(p[4])
        p[0] = ptg.four_child_node("annotation_type_declaration_header_name", p[1], tmp1, tmp2, tmp3)

    def p_annotation_type_declaration_header_name2(self, p):
        '''annotation_type_declaration_header_name : modifiers '@' INTERFACE NAME type_parameters'''
        tmp1 = ptg.node_create("@")
        tmp2 = ptg.node_create(p[3])
        tmp3 = ptg.node_create(p[4])
        p[0] = ptg.five_child_node("annotation_type_declaration_header_name", p[1], tmp1, tmp2, tmp3, p[5])

    def p_annotation_type_declaration_header_name3(self, p):
        '''annotation_type_declaration_header_name : '@' INTERFACE NAME type_parameters'''
        tmp1 = ptg.node_create("@")
        tmp2 = ptg.node_create(p[2])
        tmp3 = ptg.node_create(p[3])
        p[0] = ptg.four_child_node("annotation_type_declaration_header_name", tmp1, tmp2, tmp3, p[4])

    def p_annotation_type_declaration_header_name4(self, p):
        '''annotation_type_declaration_header_name : '@' INTERFACE NAME'''
        tmp1 = ptg.node_create("@")
        tmp2 = ptg.node_create(p[2])
        tmp3 = ptg.node_create(p[3])
        p[0] = ptg.three_child_node("annotation_type_declaration_header_name", tmp1, tmp2, tmp3)

    def p_annotation_type_body(self, p):
        '''annotation_type_body : '{' annotation_type_member_declarations_opt '}' '''
        lbrace = ptg.node_create("{")
        rbrace = ptg.node_create("}")
        p[0] = ptg.three_child_node("annotation_type_body", lbrace, p[2], rbrace)

    def p_annotation_type_member_declarations_opt(self, p):
        '''annotation_type_member_declarations_opt : annotation_type_member_declarations'''
        p[0] = ptg.one_child_node("annotation_type_member_declarations_opt", p[1])

    def p_annotation_type_member_declarations_opt2(self, p):
        '''annotation_type_member_declarations_opt : empty'''
        p[0] = ptg.one_child_node("annotation_type_member_declarations_opt", p[1])

    def p_annotation_type_member_declarations(self, p):
        '''annotation_type_member_declarations : annotation_type_member_declaration
                                               | annotation_type_member_declarations annotation_type_member_declaration'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("annotation_type_member_declarations", p[1])
        else:
            p[0] = ptg.two_child_node("annotation_type_member_declarations", p[1], p[2])

    def p_annotation_type_member_declaration(self, p):
        '''annotation_type_member_declaration : annotation_method_header ';'
                                              | constant_declaration
                                              | constructor_declaration
                                              | type_declaration'''
        p[0] = ptg.one_child_node("annotation_type_member_declaration", p[1])

    def p_annotation_method_header(self, p):
        '''annotation_method_header : annotation_method_header_name formal_parameter_list_opt ')' method_header_extended_dims annotation_method_header_default_value_opt'''
        tmp = ptg.node_create(")")
        p[0] = ptg.five_child_node("annotation_method_header", p[1], p[2], tmp, p[4], p[5])

    def p_annotation_method_header_name(self, p):
        '''annotation_method_header_name : modifiers_opt type_parameters type NAME '('
                                         | modifiers_opt type NAME '(' '''
        if len(p) == 5:
            tmp1 = ptg.node_create("(")
            tmp2 = ptg.node_create(p[3])
            p[0] = ptg.four_child_node("annotation_method_header_name", p[1], p[2], tmp1, tmp2)
        else:
            tmp1 = ptg.node_create("(")
            tmp2 = ptg.node_create(p[4])
            p[0] = ptg.five_child_node("annotation_method_header_name", p[1], p[2], p[3], tmp1, tmp2)

    def p_annotation_method_header_default_value_opt(self, p):
        '''annotation_method_header_default_value_opt : default_value
                                                      | empty'''
        p[0] = ptg.one_child_node("annotation_method_header_default_value_opt", p[1])

    def p_default_value(self, p):
        '''default_value : DEFAULT member_value'''
        tmp = ptg.node_create(p[1])
        p[0] = ptg.two_child_node("default_value", tmp, p[2])

    def p_member_value(self, p):
        '''member_value : conditional_expression_not_name
                        | name
                        | annotation
                        | member_value_array_initializer'''
        p[0] = ptg.one_child_node("member_value", p[1])

    def p_member_value_array_initializer(self, p):
        '''member_value_array_initializer : '{' member_values ',' '}'
                                          | '{' member_values '}' '''
        if len(p) == 4:
            lbrace = ptg.node_create("{")
            rbrace = ptg.node_create("}")
            p[0] = ptg.three_child_node("member_value_array_initializer", lbrace, p[2], rbrace)
        elif len(p) == 5:
            lbrace = ptg.node_create("{")
            rbrace = ptg.node_create("}")
            tmp = ptg.node_create("\,")
            p[0] = ptg.four_child_node("member_value_array_initializer", lbrace, p[2], tmp, rbrace)

    def p_member_value_array_initializer2(self, p):
        '''member_value_array_initializer : '{' ',' '}'
                                          | '{' '}' '''
        if len(p) == 3:
            lbrace = ptg.node_create("{")
            rbrace = ptg.node_create("}")
            p[0] = ptg.two_child_node("member_value_array_initializer", lbrace, rbrace)
        elif len(p) == 4:
            lbrace = ptg.node_create("{")
            rbrace = ptg.node_create("}")
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("member_value_array_initializer", lbrace, tmp, rbrace)

    def p_member_values(self, p):
        '''member_values : member_value
                         | member_values ',' member_value'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("member_values", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("member_values",  p[1], tmp, p[3])

    def p_annotation(self, p):
        '''annotation : normal_annotation
                      | marker_annotation
                      | single_member_annotation'''
        p[0] = ptg.one_child_node("annotation", p[1])

    def p_normal_annotation(self, p):
        '''normal_annotation : annotation_name '(' member_value_pairs_opt ')' '''
        lparen = ptg.node_create("(")
        rparen = ptg.node_create(")")
        p[0] = ptg.four_child_node("normal_annotation", p[1], lparen, p[3], rparen)

    def p_annotation_name(self, p):
        '''annotation_name : '@' name'''
        tmp = ptg.node_create("@")
        p[0] = ptg.two_child_node("annotation_name", tmp, p[2])

    def p_member_value_pairs_opt(self, p):
        '''member_value_pairs_opt : member_value_pairs'''
        p[0] = ptg.one_child_node("member_value_pairs_opt", p[1])

    def p_member_value_pairs_opt2(self, p):
        '''member_value_pairs_opt : empty'''
        p[0] = ptg.one_child_node("member_value_pairs_opt", p[1])

    def p_member_value_pairs(self, p):
        '''member_value_pairs : member_value_pair
                              | member_value_pairs ',' member_value_pair'''
        if len(p) == 2:
            p[0] = ptg.one_child_node("member_value_pairs", p[1])
        else:
            tmp = ptg.node_create("\,")
            p[0] = ptg.three_child_node("member_value_pairs",  p[1], tmp, p[3])

    def p_member_value_pair(self, p):
        '''member_value_pair : simple_name '=' member_value'''
        tmp = ptg.node_create("=")
        p[0] = ptg.three_child_node("member_value_pair", p[1], tmp, p[3])

    def p_marker_annotation(self, p):
        '''marker_annotation : annotation_name'''
        p[0] = ptg.one_child_node("marker_annotation", p[1])

    def p_single_member_annotation(self, p):
        '''single_member_annotation : annotation_name '(' single_member_annotation_member_value ')' '''
        lparen = ptg.node_create("(")
        rparen = ptg.node_create(")")
        p[0] = ptg.four_child_node("single_member_annotation", p[1], lparen, p[3], rparen)

    def p_single_member_annotation_member_value(self, p):
        '''single_member_annotation_member_value : member_value'''
        p[0] = ptg.one_child_node("single_member_annotation_member_value", p[1])

class CompilationUnitParser(object):

    def p_compilation_unit(self, p):
        '''compilation_unit : package_declaration'''
        p[0] = p[1]

    def p_compilation_unit2(self, p):
        '''compilation_unit : package_declaration import_declarations'''
        p[0] = p[1]

    def p_compilation_unit3(self, p):
        '''compilation_unit : package_declaration import_declarations type_declarations'''
        p[0] = Node("CompilationUnit", children=[p[1], p[2], p[3]])
        if p[3].type == "error":
            p[0].type = "error"

    def p_compilation_unit4(self, p):
        '''compilation_unit : package_declaration type_declarations'''
        p[0] = Node("CompilationUnit", children=[p[1], p[2]])
        if p[2].type == "error":
            p[0].type = "error"

    def p_compilation_unit5(self, p):
        '''compilation_unit : import_declarations'''
        p[1].name = "CompilationUnit"
        p[0] = p[1]

    def p_compilation_unit6(self, p):
        '''compilation_unit : type_declarations'''
        p[1].name = "CompilationUnit"
        p[0] = p[1]

    def p_compilation_unit7(self, p):
        '''compilation_unit : import_declarations type_declarations'''
        p[0] = Node("CompilationUnit", children=[p[1]]+p[2].children)
        if p[2].type == "error":
            p[0].type = "error"

    def p_compilation_unit8(self, p):
        '''compilation_unit : empty'''
        p[0] = p[1]

    def p_package_declaration(self, p):
        '''package_declaration : package_declaration_name ';' '''
        p[1].name = "PackageDecl"
        p[0] = p[1]

    def p_package_declaration_name(self, p):
        '''package_declaration_name : modifiers PACKAGE name
                                    | PACKAGE name'''
        if len(p) == 3:
            p[0] = Node("Package", children=[p[2]])
        else:
            p[0] = Node("Package", children=[p[3]], modifiers=p[1].modifiers)

    def p_import_declarations(self, p):
        '''import_declarations : import_declaration
                               | import_declarations import_declaration'''
        if len(p) == 2:
            p[0] = Node("ImportDecls", children=[p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_import_declaration(self, p):
        '''import_declaration : single_type_import_declaration
                              | type_import_on_demand_declaration
                              | single_static_import_declaration
                              | static_import_on_demand_declaration'''
        p[0] = p[1]

    def p_single_type_import_declaration(self, p):
        '''single_type_import_declaration : IMPORT name ';' '''
        p[0] = Node("Import", children=[p[2]])

    def p_type_import_on_demand_declaration(self, p):
        '''type_import_on_demand_declaration : IMPORT name '.' '*' ';' '''
        p[0] = Node("ImportDemand", children=[p[2]])

    def p_single_static_import_declaration(self, p):
        '''single_static_import_declaration : IMPORT STATIC name ';' '''
        p[0] = Node("StaticImport", tmp1, tmp2, p[3], tmp3)

    def p_static_import_on_demand_declaration(self, p):
        '''static_import_on_demand_declaration : IMPORT STATIC name '.' '*' ';' '''
        p[0] = Node("StaticImportDemand", children=[p[3]])

    def p_type_declarations(self, p):
        '''type_declarations : type_declaration
                             | type_declarations type_declaration'''
        if len(p) == 2:
            p[0] = Node(type=p[1].type, children=[p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
            if p[2].type == "error":
                p[0].type = "error"

class JavaParser(ExpressionParser, NameParser, LiteralParser, TypeParser, ClassParser, StatementParser, CompilationUnitParser):
    tokens = lexer.tokens

    def p_goal_compilation_unit(self, p):
        '''goal : PLUSPLUS compilation_unit'''
        p[0] = p[2]
        p[0].print_tree()
        target = open("ast.txt", 'w')
        target.write(ast)
        target.close()
        p[0].print_png()

    def p_goal_expression(self, p):
        '''goal : MINUSMINUS expression'''
        p[0] = p[2]
        p[0].print_tree()
        target = open("ast.txt", 'w')
        target.write(ast)
        target.close()
        p[0].print_png()

    def p_goal_statement(self, p):
        '''goal : '*' block_statement'''
        p[0] = p[2]

    # Error rule for syntax errors
    def p_error(self, p):
        print('error: {}'.format(p))

    def p_empty(self, p):
        '''empty :'''
        p[0] = Node()

    def p_begin_scope(self, p):
        '''begin_scope : '''
        symbol_table.begin_scope()

    def p_end_scope(self, p):
        '''end_scope : '''
        symbol_table.end_scope()
