class bubblesort {
    void sort(int[] arr, int len) {
        int n = len;
        int temp, i, j;
        for(i=0; i < n; i++){
            for(j=1; j < (n-i); j++){
                if(arr[j-1] > arr[j]){
                    temp = arr[j-1];  
                    arr[j-1] = arr[j];  
                    arr[j] = temp;  
                }  
            }
        }
    }  
    public static void main() {
                char c = 10;
                int arr[] ={7,6,5,4,3,2,1};
                printString("unsorted: ");
                for(int i=0; i < 7; i++){  
                        printInt(arr[i]);  
                }  
                printChar(c);
                sort(arr, 7);//sorting array elements using bubble sort  
                printString("sorted: ");
                for(int i=0; i < 7; i++){  
                        printInt(arr[i]);  
                }  
                printChar(c);
   
        }  
} 
