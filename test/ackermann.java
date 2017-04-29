class ackermann{
    int Ack(int m,int n) {
        int i = -1;
        if (m>=0 && n>=0) {
            if (m == 0) {
                i = n + 1;
            } else if (n == 0) {
                i = Ack(m - 1, 1);
            } else {
                i = Ack(m - 1, Ack(m, n - 1));
            }
        }
        return i;
    }
    public static void main(){
        int i = Ack(1,2);
        printInt(i);
    }
}
