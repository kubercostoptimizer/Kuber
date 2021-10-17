import java.io.IOException;
import java.util.Calendar;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.HashMap;
import java.util.Arrays;
import java.util.Date;

public class Example {
   static boolean isprimenumber(int num) {
      boolean flag = false;
      for (int i = 2; i <= num / 2; ++i) {
        // condition for nonprime number
        if (num % i == 0) {
          flag = true;
          break;
        }
      }
  
      if (!flag)
        return true;
      else
        return false;
   }
   static void test() {
      for (int i = 0; i<20000; i++)
      {
         isprimenumber(i);
      }
   }
   
   public static void main(String[] args) {

    long[] duration = new long[100];
    for(int i = 0; i< 100; i++)
    {
       long startTime = System.nanoTime();
       test();
       long endTime = System.nanoTime();
       duration[i] = (endTime - startTime)/1000;
    }
    System.out.println(Arrays.toString(duration));
   }
}
