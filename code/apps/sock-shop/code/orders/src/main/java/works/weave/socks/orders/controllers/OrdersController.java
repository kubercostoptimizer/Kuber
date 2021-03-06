package works.weave.socks.orders.controllers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.data.rest.webmvc.RepositoryRestController;
import org.springframework.hateoas.Resource;
import org.springframework.hateoas.mvc.TypeReferences;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import works.weave.socks.orders.config.OrdersConfigurationProperties;
import works.weave.socks.orders.entities.*;
import works.weave.socks.orders.repositories.CustomerOrderRepository;
import works.weave.socks.orders.resources.NewOrderResource;
import works.weave.socks.orders.services.AsyncGetService;
import works.weave.socks.orders.values.PaymentRequest;
import works.weave.socks.orders.values.PaymentResponse;

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

@RepositoryRestController
public class OrdersController {
    private final Logger LOG = LoggerFactory.getLogger(getClass());

    @Autowired
    private OrdersConfigurationProperties config;

    @Autowired
    private AsyncGetService asyncGetService;

    @Autowired
    private CustomerOrderRepository customerOrderRepository;

    @Value(value = "${http.timeout:5}")
    private long timeout;
    private static String getProperty(String name) {
       return System.getProperty(name, System.getenv(name));
    }
    @ResponseStatus(HttpStatus.CREATED)
    @RequestMapping(path = "/orders", consumes = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.POST)
    public
    @ResponseBody
    CustomerOrder newOrder(@RequestBody NewOrderResource item) {
        
        System.out.println("Start of newOrder\n");
        Tracer tracer = Configuration.fromEnv().getTracer();
        Span span = tracer.buildSpan("newOrder").start();
        long startTime = System.nanoTime();
        System.out.println("line 65 time " + Long.toString((System.nanoTime()-startTime)/1000));
        long external_time = 0;
        long extstartTime = 0;
        System.out.println("line 67 time " + Long.toString((System.nanoTime()-startTime)/1000));
        try {

            if (item.address == null || item.customer == null || item.card == null || item.items == null) {
                throw new InvalidOrderException("Invalid order request. Order requires customer, address, card and items.");
            }

            Future<Resource<Address>> addressFuture = asyncGetService.getResource(item.address, new TypeReferences.ResourceType<Address>() {});
            System.out.println("line 77 time " + Long.toString((System.nanoTime()-startTime)/1000));

            Future<Resource<Customer>> customerFuture = asyncGetService.getResource(item.customer, new TypeReferences.ResourceType<Customer>() {});
            System.out.println("line 83 time " + Long.toString((System.nanoTime()-startTime)/1000));

            Future<Resource<Card>> cardFuture = asyncGetService.getResource(item.card, new TypeReferences.ResourceType<Card>() {});
            System.out.println("line 89 time " + Long.toString((System.nanoTime()-startTime)/1000));

            Future<List<Item>> itemsFuture = asyncGetService.getDataList(item.items, new ParameterizedTypeReference<List<Item>>() {});
            System.out.println("line 95 time " + Long.toString((System.nanoTime()-startTime)/1000));

            extstartTime = System.nanoTime();
            List<Item> items = itemsFuture.get(timeout, TimeUnit.SECONDS); 
            external_time = external_time + System.nanoTime() - extstartTime; 
            System.out.println("itemsFuture external call " + Long.toString((System.nanoTime()-startTime-external_time)/1000));

            float amount = calculateTotal(items);
            
            System.out.println("itemsFuture external call " + Long.toString((System.nanoTime()-startTime-external_time)/1000));

            extstartTime = System.nanoTime();
            PaymentRequest paymentRequest = new PaymentRequest(addressFuture.get(timeout, TimeUnit.SECONDS).getContent(), cardFuture.get(timeout, TimeUnit.SECONDS).getContent(), customerFuture.get(timeout, TimeUnit.SECONDS).getContent(), amount);
            external_time = external_time + System.nanoTime() - extstartTime;
            System.out.println("paymentRequest external call " + Long.toString((System.nanoTime()-startTime-external_time)/1000)); 
         
            // LOG.info("Sending payment request: " + paymentRequest);
            Future<PaymentResponse> paymentFuture = asyncGetService.postResource(config.getPaymentUri(), paymentRequest, new ParameterizedTypeReference<PaymentResponse>() {});

            extstartTime = System.nanoTime();
            PaymentResponse paymentResponse = paymentFuture.get(timeout, TimeUnit.SECONDS);
            external_time = external_time + System.nanoTime() - extstartTime;
            System.out.println("paymentFuture external call " + Long.toString((System.nanoTime()-startTime-external_time)/1000));  


            // LOG.info("Received payment response: " + paymentResponse);
            if (paymentResponse == null) { throw new PaymentDeclinedException("Unable to parse authorisation packet");}
            if (!paymentResponse.isAuthorised()) { throw new PaymentDeclinedException(paymentResponse.getMessage());}
            // Ship
            extstartTime = System.nanoTime();
            String customerId = parseId(customerFuture.get(timeout, TimeUnit.SECONDS).getId().getHref());
            external_time = external_time + System.nanoTime() - extstartTime;
            System.out.println("customerFuture external call " + Long.toString((System.nanoTime()-startTime-external_time)/1000));  
 

            Future<Shipment> shipmentFuture = asyncGetService.postResource(config.getShippingUri(), new Shipment(customerId), new ParameterizedTypeReference<Shipment>() {});

            extstartTime = System.nanoTime();
            CustomerOrder order = new CustomerOrder(null, customerId, customerFuture.get(timeout, TimeUnit.SECONDS).getContent(), addressFuture.get(timeout, TimeUnit.SECONDS).getContent(), cardFuture.get(timeout, TimeUnit.SECONDS).getContent(), itemsFuture.get(timeout, TimeUnit.SECONDS), shipmentFuture.get(timeout, TimeUnit.SECONDS), Calendar.getInstance().getTime(), amount);
            // LOG.debug("Received data: " + order.toString());
            CustomerOrder savedOrder = customerOrderRepository.save(order);
            external_time = external_time + System.nanoTime() - extstartTime; 
            System.out.println("CustomerOrder external call " +Long.toString((System.nanoTime()-startTime-external_time)/1000));  

            long duration = System.nanoTime() - startTime - external_time;
            HashMap hm = new HashMap();
            System.out.println("Final duration "+ duration/1000);
            hm.put("runtime_ms",duration/1000);
            span.log(hm);
            span.finish();
            System.out.println("End of newOrder\n");
            return savedOrder;

        } catch (TimeoutException e) {
            throw new IllegalStateException("Unable to create order due to timeout from one of the services.", e);
        } catch (InterruptedException | IOException | ExecutionException e) {
            throw new IllegalStateException("Unable to create order due to unspecified IO error.", e);
        }
    }

    private String parseId(String href) {
        Pattern idPattern = Pattern.compile("[\\w-]+$");
        Matcher matcher = idPattern.matcher(href);
        if (!matcher.find()) {
            throw new IllegalStateException("Could not parse user ID from: " + href);
        }
        return matcher.group(0);
    }

//    TODO: Add link to shipping
//    @RequestMapping(method = RequestMethod.GET, value = "/orders")
//    public @ResponseBody
//    ResponseEntity<?> getOrders() {
//        List<CustomerOrder> customerOrders = customerOrderRepository.findAll();
//
//        Resources<CustomerOrder> resources = new Resources<>(customerOrders);
//
//        resources.forEach(r -> r);
//
//        resources.add(linkTo(methodOn(ShippingController.class, CustomerOrder.getShipment::ge)).withSelfRel());
//
//        // add other links as needed
//
//        return ResponseEntity.ok(resources);
//    }

    private float calculateTotal(List<Item> items) {
        float amount = 0F;
        float shipping = 4.99F;
        amount += items.stream().mapToDouble(i -> i.getQuantity() * i.getUnitPrice()).sum();
        amount += shipping;
        return amount;
    }

    @ResponseStatus(value = HttpStatus.NOT_ACCEPTABLE)
    public class PaymentDeclinedException extends IllegalStateException {
        public PaymentDeclinedException(String s) {
            super(s);
        }
    }

    @ResponseStatus(value = HttpStatus.NOT_ACCEPTABLE)
    public class InvalidOrderException extends IllegalStateException {
        public InvalidOrderException(String s) {
            super(s);
        }
    }
}
