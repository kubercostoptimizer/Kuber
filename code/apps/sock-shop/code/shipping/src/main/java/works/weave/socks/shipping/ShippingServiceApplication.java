package works.weave.socks.shipping;

import io.opentracing.*;
import io.opentracing.util.GlobalTracer;
import io.jaegertracing.Configuration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ShippingServiceApplication {
    public static void main(String[] args) throws InterruptedException {
        Tracer tracer = Configuration.fromEnv().getTracer();
        GlobalTracer.registerIfAbsent(tracer);
        SpringApplication.run(ShippingServiceApplication.class, args);
    }
}
