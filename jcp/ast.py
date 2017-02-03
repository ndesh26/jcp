import pydot

graph = pydot.Dot(graph_type='graph')

k = 0

def three_child_node(label, node1_id, node2_id, node3_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))

    return k

def two_child_node(label, node1_id, node2_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))

    return k

def one_child_node(label, node_id):
    global k
    node = pydot.Node(node_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)
    graph.add_edge(pydot.Edge(parent_node, node))

    return k

def node_create(label):
    global k
    k+=1
    node = pydot.Node(k,label=label)

    graph.add_node(node)

    return k

def end():
    graph.write_png('example1_graph.png')
