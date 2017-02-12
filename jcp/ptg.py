import pydot

graph = pydot.Dot(graph_type='graph')

k = 0
def nine_child_node(label, node1_id, node2_id, node3_id, node4_id, node5_id, node6_id, node7_id, node8_id, node9_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    node5 = pydot.Node(node5_id)
    node6 = pydot.Node(node6_id)
    node7 = pydot.Node(node7_id)
    node8 = pydot.Node(node8_id)
    node9 = pydot.Node(node9_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))
    graph.add_edge(pydot.Edge(parent_node, node5))
    graph.add_edge(pydot.Edge(parent_node, node6))
    graph.add_edge(pydot.Edge(parent_node, node7))
    graph.add_edge(pydot.Edge(parent_node, node8))
    graph.add_edge(pydot.Edge(parent_node, node9))

    return k

def eight_child_node(label, node1_id, node2_id, node3_id, node4_id, node5_id, node6_id, node7_id, node8_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    node5 = pydot.Node(node5_id)
    node6 = pydot.Node(node6_id)
    node7 = pydot.Node(node7_id)
    node8 = pydot.Node(node8_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))
    graph.add_edge(pydot.Edge(parent_node, node5))
    graph.add_edge(pydot.Edge(parent_node, node6))
    graph.add_edge(pydot.Edge(parent_node, node7))
    graph.add_edge(pydot.Edge(parent_node, node8))

    return k

def seven_child_node(label, node1_id, node2_id, node3_id, node4_id, node5_id, node6_id, node7_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    node5 = pydot.Node(node5_id)
    node6 = pydot.Node(node6_id)
    node7 = pydot.Node(node7_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))
    graph.add_edge(pydot.Edge(parent_node, node5))
    graph.add_edge(pydot.Edge(parent_node, node6))
    graph.add_edge(pydot.Edge(parent_node, node7))

    return k

def six_child_node(label, node1_id, node2_id, node3_id, node4_id, node5_id, node6_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    node5 = pydot.Node(node5_id)
    node6 = pydot.Node(node6_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))
    graph.add_edge(pydot.Edge(parent_node, node5))
    graph.add_edge(pydot.Edge(parent_node, node6))

    return k

def five_child_node(label, node1_id, node2_id, node3_id, node4_id, node5_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    node5 = pydot.Node(node5_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))
    graph.add_edge(pydot.Edge(parent_node, node5))

    return k

def four_child_node(label, node1_id, node2_id, node3_id, node4_id):
    global k
    node1 = pydot.Node(node1_id)
    node2 = pydot.Node(node2_id)
    node3 = pydot.Node(node3_id)
    node4 = pydot.Node(node4_id)
    k+=1
    parent_node = pydot.Node(k,label=label)

    graph.add_node(parent_node)

    graph.add_edge(pydot.Edge(parent_node, node1))
    graph.add_edge(pydot.Edge(parent_node, node2))
    graph.add_edge(pydot.Edge(parent_node, node3))
    graph.add_edge(pydot.Edge(parent_node, node4))

    return k

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
