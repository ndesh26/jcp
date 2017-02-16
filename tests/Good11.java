// To check the structure of if-else statement:
import java.util.*;

public class Good11{
    public static void main(String[] args){
        int x;
        System.out.println("Enter a value");
        Scanner sc = new Scanner(System.in);
        x = sc.nextInt();
        if(x > 0)
            System.out.printf("%d", x);
        else
            System.out.printf("Number is zero");
    }
}
