class ifib{
    int ifib (int n) {
        int f1 = 0;
        int f2 = 1;
        int fn;
        if (n==0) {
            fn = 0;
        }
        else if (n==1) {
            fn = 1;
        }
        for (int i=1;i<n;i++) {
            fn = f1 + f2;
            f1 = f2;
            f2 = fn;
        }
        return fn;
    }
    public static void main() {
        printInt(ifib(0));
        printInt(ifib(1));
        printInt(ifib(2));
        printInt(ifib(3));
        printInt(ifib(4));
        printInt(ifib(5));
        printInt(ifib(6));
        printInt(ifib(7));
    }
}
