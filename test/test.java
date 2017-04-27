class main {
    int fact(int a){
        if (a==1)
            return 1;
        return a*fact(a-1);
    };
     int main() {
         int a = 5;
         printInt(fact(6));
         return a;
    }

}

