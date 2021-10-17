package works.weave.socks.cart;

import io.opentracing.*;
import io.opentracing.util.GlobalTracer;
import io.jaegertracing.Configuration;

import io.prometheus.client.spring.boot.EnablePrometheusEndpoint;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@EnablePrometheusEndpoint
public class CartApplication {
    public static void main(String[] args) {
        Tracer tracer = Configuration.fromEnv().getTracer();
        GlobalTracer.registerIfAbsent(tracer);
        SpringApplication.run(CartApplication.class, args);
    }
}
