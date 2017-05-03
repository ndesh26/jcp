class array{
    void nayan(int[] x, int l){
        int i;
        printInt(x[0]);
        x[0] = 6;
    }

    public static void main(){
        int x[] = {1,2,3,4};
        x[0] = 5;
        nayan(x, 5);
        printInt(x[0]);
    }
}
