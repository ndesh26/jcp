//Good testcase - Syntax check for nested - if else
public class Good4{
    public static void main(String[] args){
        int a = 0;
        if(a == 0){
            System.out.printf("if");
            if(a > b){
                System.out.printf("nested if");
            }
            else{
                System.out.printf(" nested else");
            }
        }
    }
}
