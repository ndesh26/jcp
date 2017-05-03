class main {
    public void main() {
        int i,j;
        for (i = 1; i < 5; i++){
            printlnInt(i);
            if (i > 2)
                break;
        }

        for (i = 1; i < 5; i++){
            if (i >= 2 && i <= 3)
                continue;
            else
                printlnInt(i);
        }
    }
}
