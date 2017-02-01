import pydot

graph = pydot.Dot(graph_type='graph')

k = 0

def binary_op(op_label, node1_id, node2_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    k+=1
    node_op = pydot.Node(k,label=op_label)

    graph.add_node(node_op)

    graph.add_edge(pydot.Edge(node_op, node1))
    graph.add_edge(pydot.Edge(node_op, node2))

    return k 

def single_node(label):
    global k
    k+=1
    node = pydot.Node(k,label=label)

    graph.add_node(node)

    return k

def end():
    graph.write_png('example1_graph.png')
