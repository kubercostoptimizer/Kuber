package works.weave.socks.cart.controllers;

import io.opentracing.Scope;
import io.jaegertracing.Configuration;
import io.opentracing.Span;
import io.opentracing.Tracer;
import io.opentracing.log.Fields;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import works.weave.socks.cart.cart.CartDAO;
import works.weave.socks.cart.cart.CartResource;
import works.weave.socks.cart.entities.Cart;
import java.util.concurrent.TimeUnit;
import java.util.*;

@RestController
@RequestMapping(path = "/carts")
public class CartsController {
    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    Tracer tracer = Configuration.fromEnv().getTracer();

    @Autowired
    private CartDAO cartDAO;

    @ResponseStatus(HttpStatus.OK)
    @RequestMapping(value = "/{customerId}", produces = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.GET)
    public Cart get(@PathVariable String customerId) {
        long startTime = System.nanoTime();
        final Span span = tracer.buildSpan("get_cart").start();
        Cart obj = new CartResource(cartDAO, customerId).value().get();
        long duration = System.nanoTime() - startTime;
        HashMap hm = new HashMap();
        hm.put("runtime_ms",duration/1000);
        System.out.println("get call took "+duration);
        span.log(hm);
        span.finish();
        return obj;
        
    }

    @ResponseStatus(HttpStatus.ACCEPTED)
    @RequestMapping(value = "/{customerId}", method = RequestMethod.DELETE)
    public void delete(@PathVariable String customerId) {
        long startTime = System.nanoTime();
        final Span span = tracer.buildSpan("delete").start();
        new CartResource(cartDAO, customerId).destroy().run();
        long duration = System.nanoTime() - startTime;
        HashMap hm = new HashMap();
        hm.put("runtime_ms",duration/1000);
        System.out.println("delete call took "+duration);
        span.log(hm);
        span.finish();
    }

    @ResponseStatus(HttpStatus.ACCEPTED)
    @RequestMapping(value = "/{customerId}/merge", method = RequestMethod.GET)
    public void mergeCarts(@PathVariable String customerId, @RequestParam(value = "sessionId") String sessionId) {
        
        long startTime = System.nanoTime();
        final Span span = tracer.buildSpan("merge").start();
        logger.debug("Merge carts request received for ids: " + customerId + " and " + sessionId);
        CartResource sessionCart = new CartResource(cartDAO, sessionId);
        CartResource customerCart = new CartResource(cartDAO, customerId);
        customerCart.merge(sessionCart.value().get()).run();
        delete(sessionId);
        long duration =  System.nanoTime() - startTime;
        HashMap hm = new HashMap();
        hm.put("runtime_ms",duration/1000);
        System.out.println("mergeCarts call took "+duration);
        span.log(hm);
        span.finish();
    }
}
