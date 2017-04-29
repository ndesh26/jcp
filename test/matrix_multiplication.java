class matrix_multiplication{
    public static void main(){
        int i, j, k;
        int firstarray[][] = {{1, 2, -2, 0}, {-3, 4, 7, 2}, {6, 0, 3, 1}};
        int secondarray[][] = {{-1, 3}, {0, 9}, {1, -11}, {4, -5}};
        /* Create another 2d array to store the result using the original arrays' lengths on row and column respectively. */
        int [][] result = new int[3][2];
        for (i = 0; i < 3; i++) {
            for (k = 0; k < 2; k++) {
                result[i][k] = 0;
            }
        }
        /* Loop through each and get product, then sum up and store the value */
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 2; j++) {
                for (k = 0; k < 4; k++) {
                    result[i][j] =  result[i][j] + firstarray[i][k] * secondarray[k][j];
                }
            }
        }
        char c = ' ';
        /* Show the result */
        for (i = 0; i < 3; i++) {
            for (k = 0; k < 2; k++) {
                printInt(result[i][k]);
                printChar(c);
            }
            printChar(c);
        }
    }
}
