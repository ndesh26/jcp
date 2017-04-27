class Qsort
{
	public static int quicksort(int[] x, int first, int last){
		int pivot,j,temp,i,f,e,a;

		if(first<last){
			pivot=first;
			i=first;
			j=last;

			while(i<j){

				while((x[i] <= x[pivot]) && (i < last)){
					i= i + 1;
				}
				while(x[j]>x[pivot]){
					j= j - 1;
				}
				if(i<j){
					temp=x[i];
					x[i]=x[j];
					x[j]=temp;
				}
			}

			temp=x[pivot];
			x[pivot]=x[j];
			x[j]=temp;
			f = j - 1 ;
			e = j + 1;

			quicksort(x,first,f);
			quicksort(x,e,last);

		}
		return 0;
	}

	public static void main(){
		int[] x = new int[5];
		int size = 5;
		int first = 0;
		int l = size - 1;
		int i;

		x[0] = 2;
		x[1] = 1;
		x[3] = 5;
		x[4] = 6;
		x[2] = 0;

		// for(i=0;i<size;i++){
			// System.out.println(l);
		// }
		quicksort(x,first,l);

		for(i=0;i<size;i++){
			printInt(x[i]);
		}
	}

}
