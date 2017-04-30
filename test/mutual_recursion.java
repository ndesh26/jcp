class mutual_recursion{
    int even_function(int n);
    int odd_function(int n){
        int odd;
        if (n==1){
            odd = 1;
        }
        else{
            odd = even_function(n-1);
        }
        return odd;
    }
    int even_function(int n){
        int even;
        if (n==1){
            even = 0;
        }
        else{
            even = odd_function(n-1);
        }
        return even;
    }
    public static void main(){
        printInt(even_function(8));
    }
}
