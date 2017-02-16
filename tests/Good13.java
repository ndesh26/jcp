// This test is to test the user-defined data type.
// typedef int myint; /* here myint should be identifier*/
// myint a; /* Here myint should be Data Type*/ // By- Nishit
class long_int{
    long z = 5;
    String s;
}

public class Good9 extends long_int{
    public static void main(String[] args){
        long_int l = new long_int();
        long x = l.z + 5;
        System.out.printf("Size for lon long int data type     : %ld \n", x);
    }
}
