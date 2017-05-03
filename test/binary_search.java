public class MyBinarySearch {
    public int binarySearch(int[] inputArr, int len, int key) {
        int start = 0,mid;
        int end = len - 1;
        while (start <= end) {
            mid = (start + end) / 2;
            if (key == inputArr[mid]) {
                return mid;
            }
            if (key < inputArr[mid]) {
                end = mid - 1;
            } else {
                start = mid + 1;
            }
        }
        return -1;
    }
    public static void main() {
        //MyBinarySearch mbs = new MyBinarySearch();
        int[] arr = {2, 4, 6, 8, 10, 12, 14, 16};
        printlnInt(binarySearch(arr, 8, 14));
        int[] arr1 = {6,34,78,123,432,900};
        printlnInt(binarySearch(arr1, 6, 432));
    }
}
