//Bad test case for parsing - if -else ladder violated
class Bad5 {
    void main(){
    	int a = 0;
    	if(a == 0){
        		printf("if");
    	}else{
        		printf(" 1st else");
    	}else{
        		printf("Error 'else' without a previous 'if' ");
    	}
    }
}
