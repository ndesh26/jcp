class matrix_multiplication{
    public static void main(){
        int i, j, k;
        int firstarray[][] = new int[3][4];
        int secondarray[][] = new int[4][2];

        /* Initialize the array 1 */
        firstarray[0][0] = 1; firstarray[0][1] = 2; firstarray[0][2] = -2; firstarray[0][3] = 0;
        firstarray[1][0] = -3; firstarray[1][1] = 4; firstarray[1][2] = 7; firstarray[1][3] = 2;
        firstarray[2][0] = 6; firstarray[2][1] = 0; firstarray[2][2] = 3; firstarray[2][3] = 1;

        /* Initialize the array 1 */
        secondarray[0][0] = -1; secondarray[0][1] = 3;
        secondarray[1][0] = 0; secondarray[1][1] = 9;
        secondarray[2][0] = 1; secondarray[2][1] = -11;
        secondarray[3][0] = 4; secondarray[3][1] = -5;

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
        char c = 10;
        /* Show the result */
        for (i = 0; i < 3; i++) {
            for (k = 0; k < 2; k++) {
                printInt(result[i][k]);
                printChar(' ');
            }
            printChar(c);
        }
    }
}
