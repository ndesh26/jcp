class Node{
    int data;
    Node left;
    Node right;
    public Node(int d, Node l, Node r){
        this.data = d;
        left = l;
        right = r;
    }
}

class BinaryTree {
    public void printTree(Node n) {
        if (n.left != null)
            printTree(n.left);
        printInt(n.data);
        if (n.right != null)
            printTree(n.right);
    }

    public static void main(){
        Node left_child = new Node(6, null, null);
        Node right_child = new Node(8, null, null);
        Node root2 = new Node(7, left_child, right_child);
        Node left_child1 = new Node(2, null, null);
        Node right_child1 = new Node(4, null, null);
        Node root1 = new Node(3, left_child1, right_child1);
        Node root = new Node(5, root1, root2);

        printTree(root);
        char n = 10;
        printChar(n);
    }
}
