import ply.yacc as yacc
import pydot

from lexer import tokens

graph = pydot.Dot(graph_type='graph')
k = 0

def p_expression_plus(p):
    '''term : NUMBER PLUS NUMBER'''
    global k
    node_b = pydot.Node(k,label=p[1])
    k+=1
    node_c = pydot.Node(k,label="+")
    k+=1
    node_d = pydot.Node(k,label=p[3])
    k+=1

    graph.add_node(node_b)
    graph.add_node(node_c)
    graph.add_node(node_d)

    graph.add_edge(pydot.Edge(node_b, node_c))
    graph.add_edge(pydot.Edge(node_c, node_d))

def p_expression_minus(p):
    'term : NUMBER MINUS NUMBER'
    print(p[1]+"-"+p[3])

# Build the parser
parser = yacc.yacc()

while True:
   try:
       s = input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   graph.write_png('example2_graph.png')
