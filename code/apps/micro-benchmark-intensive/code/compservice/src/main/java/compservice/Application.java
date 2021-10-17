package comservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.ResponseBody;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.hateoas.Resource;
import org.springframework.hateoas.mvc.TypeReferences;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;

import io.opentracing.*;
import io.jaegertracing.Configuration;

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

@SpringBootApplication
@RestController
public class Application {

  long []durations;
  int req_index;
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

  @RequestMapping("/run")
  @ResponseBody
  public String run() {
    Tracer tracer = Configuration.fromEnv().getTracer();
    Span span = tracer.buildSpan("run").start();
    long startTime = System.nanoTime();
    System.out.println("starttime "+startTime);
    for (int i = 0; i<200000; i++)
    {
      isprimenumber(i);
    }
    long endTime = System.nanoTime();
    long duration = endTime - startTime;
    System.out.println("endtime "+endTime);
    HashMap hm = new HashMap();
    System.out.println("Final duration "+ duration/1000);
    hm.put("runtime_ms",duration/1000);
    span.log(hm);
    span.finish();
    return "1";
  }

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }

}
