class List{
    int node_value;
    List next;
    List(){
        this.next = null;
    }
}

class AdjacencyList{
    int n;
    List[] adj;
    
    AdjacencyList() {
        int i;
        adj = new List[4];
        for (i = 0; i < 4; i++) { 
            adj[i] = new List();
            adj[i].node_value = -1;
        }
    }

    void addEdge(int i, int j) {
        List node = new List();
        node.node_value = j;
        node.next = adj[i];
        adj[i] = node;
        return;
    }

    void removeEdge(int i, int j) {
        while (adj[i].next != null) {
            if (adj[i].next.node_value == j) {
                if (adj[i].next.next == null) {
                    adj[i].next = null;
                }
                else{
                    adj[i].next = adj[i].next.next;
                }
            }
        }
        return;
    }

    void printEdges(){
        List curr;
        int i;
        char c = 10;
        for (i = 0; i < 4; i++) {
            curr = adj[i];
            while (curr.next != null) {
                printInt(i);
                printChar('-');
                printChar('>');
                printInt(curr.node_value);
                printChar(c);
                curr = curr.next;
            }
        }
    }
}

class Graph{
    public static void main(){
        AdjacencyList list = new AdjacencyList();
        list.addEdge(0, 1);
        list.addEdge(0, 2);
        list.addEdge(0, 3);
        list.addEdge(1, 2);
        list.printEdges();
    }
}
