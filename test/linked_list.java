class Link {
    public int data1;
    public int data2;
    public Link nextLink;

    //Link constructor
    public Link(int d1, int d2) {
        data1 = d1;
        data2 = d2;
    }

    //Print Link data
    public void printLink() {
        printChar('{');
        printInt(data1);
        printChar(',');
        printInt(data2);
        printChar('}');
    }
}

class LinkList {
    private Link first;

    //LinkList constructor
    public LinkList() {
        first = null;
    }

    //Returns true if list is empty
    public int isEmpty() {
        int r;
        if (first == null)
            r = 1;
        else
            r = 0;
        return r;
    }

    //Inserts a new Link at the first of the list
    public void insert(int d1, int d2) {
        Link link = new Link(d1, d2);
        link.nextLink = first;
        first = link;
    }

    //Deletes the link at the first of the list
    public Link delete() {
        Link temp = first;
        first = this.first.nextLink;
        return temp;
    }

    //Prints list data
    public void printList() {
        Link currentLink = first;
        char c = 10;
        while(currentLink != null) {
            currentLink.printLink();
            currentLink = currentLink.nextLink;
        }
        printChar(c);
    }

    // search
    public int search(int a) {
        Link currentLink = first;
        int index = -1;
        while(currentLink != null) {
            if (currentLink.data2 == a) {
                index = currentLink.data1;
                break;
            }
            currentLink = currentLink.nextLink;
        }
        return index;
    }
} 

class LinkListTest {
    public static void main() {
        LinkList list = new LinkList();
        char c = 10;

        list.insert(1, 101);
        list.insert(2, 202);
        list.insert(3, 303);
        list.insert(4, 404);
        list.insert(5, 505);
        list.printList();

        printlnInt(list.search(404));
        printlnInt(list.search(405));
    }
}
