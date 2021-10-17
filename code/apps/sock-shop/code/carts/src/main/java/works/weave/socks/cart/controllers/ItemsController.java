package works.weave.socks.cart.controllers;

import io.opentracing.Scope;
import io.jaegertracing.Configuration;
import io.opentracing.Tracer;
import io.opentracing.Span;

import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import works.weave.socks.cart.cart.CartDAO;
import works.weave.socks.cart.cart.CartResource;
import works.weave.socks.cart.entities.Item;
import works.weave.socks.cart.item.FoundItem;
import works.weave.socks.cart.item.ItemDAO;
import works.weave.socks.cart.item.ItemResource;

import java.util.List;
import java.util.function.Supplier;
import java.util.Map;
import java.util.HashMap;

import static org.slf4j.LoggerFactory.getLogger;

@RestController
@RequestMapping(value = "/carts/{customerId:.*}/items")
public class ItemsController {
    private final Logger LOG = getLogger(getClass());
    Tracer tracer = Configuration.fromEnv().getTracer();
    @Autowired
    private ItemDAO itemDAO;
    @Autowired
    private CartsController cartsController;
    @Autowired
    private CartDAO cartDAO;

    @ResponseStatus(HttpStatus.OK)
    @RequestMapping(value = "/{itemId:.*}", produces = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.GET)
    public Item get(@PathVariable String customerId, @PathVariable String itemId) {
        long startTime = System.nanoTime();
        final Span span = tracer.buildSpan("get_item").start();
        Item obj = new FoundItem(() -> getItems(customerId), () -> new Item(itemId)).get();
        HashMap logm = new HashMap();
        long duration = System.nanoTime() - startTime;
        logm.put("runtime_ms",duration);
        System.out.println("get_item call took "+duration);
        span.log(logm);
        span.finish();
        return obj;
    }

    @ResponseStatus(HttpStatus.OK)
    @RequestMapping(produces = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.GET)
    public List<Item> getItems(@PathVariable String customerId) {
        long startTime = System.nanoTime();
        long totalexternaltime = 0;
        final Span span = tracer.buildSpan("getItems").start();
        long externalcalls = System.nanoTime(); 
        List<Item> obj = cartsController.get(customerId).contents();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        long duration = System.nanoTime() - startTime - totalexternaltime;
        HashMap logm = new HashMap();
        logm.put("runtime_ms",duration);
        System.out.println("getItems call took "+duration);
        span.log(logm);
        span.finish();
        return obj;
    }

    @ResponseStatus(HttpStatus.CREATED)
    @RequestMapping(consumes = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.POST)
    public Item addToCart(@PathVariable String customerId, @RequestBody Item item) {
        long startTime = System.nanoTime();
        long totalexternaltime = 0;
        final Span span = tracer.buildSpan("addToCart").start();
        // If the item does not exist in the cart, create new one in the repository.
        FoundItem foundItem = new FoundItem(() -> cartsController.get(customerId).contents(), () -> item);
        boolean hasitem;

        long externalcalls = System.nanoTime();
        hasitem = foundItem.hasItem();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        
        if (!hasitem) {
            Supplier<Item> newItem = new ItemResource(itemDAO, () -> item).create();
            LOG.debug("Did not find item. Creating item for user: " + customerId + ", " + newItem.get());
            new CartResource(cartDAO, customerId).contents().get().add(newItem).run();
            
            long duration = System.nanoTime() - startTime - totalexternaltime;
            HashMap logm = new HashMap();
            logm.put("runtime_ms",duration/1000);
            System.out.println("addToCart new call took "+duration);
            span.log(logm);
            span.finish();
            return item;
            
        } else {
            Item newItem = new Item(foundItem.get(), foundItem.get().quantity() + 1);
            LOG.debug("Found item in cart. Incrementing for user: " + customerId + ", " + newItem);

            externalcalls = System.nanoTime();
            updateItem(customerId, newItem);
            totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;            
            return newItem;
        }
    }   

    @ResponseStatus(HttpStatus.ACCEPTED)
    @RequestMapping(value = "/{itemId:.*}", method = RequestMethod.DELETE)
    public void removeItem(@PathVariable String customerId, @PathVariable String itemId) {
        long startTime = System.nanoTime();
        long totalexternaltime = 0; 
        final Span span = tracer.buildSpan("removeItem").start();
        FoundItem foundItem = new FoundItem(() -> getItems(customerId), () -> new Item(itemId));
        long externalcalls = System.nanoTime();
        Item item = foundItem.get();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        LOG.debug("Removing item from cart: " + item);
        externalcalls = System.nanoTime();
        new CartResource(cartDAO, customerId).contents().get().delete(() -> item).run();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        LOG.debug("Removing item from repository: " + item);
        externalcalls = System.nanoTime();
        new ItemResource(itemDAO, () -> item).destroy().run();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        long duration = System.nanoTime() - startTime - totalexternaltime;
        HashMap logm = new HashMap();
        logm.put("runtime_ms",duration/1000);
        System.out.println("removeItem call took "+duration);
        span.log(logm);
        span.finish();
    }

    @ResponseStatus(HttpStatus.ACCEPTED)
    @RequestMapping(consumes = MediaType.APPLICATION_JSON_VALUE, method = RequestMethod.PATCH)
    public void updateItem(@PathVariable String customerId, @RequestBody Item item) {
        long startTime = System.nanoTime(); 
        long totalexternaltime = 0;
        final Span span = tracer.buildSpan("updateItem").start();
        // Merge old and new items
        ItemResource itemResource = new ItemResource(itemDAO, () -> get(customerId, item.itemId()));
        LOG.debug("Merging item in cart for user: " + customerId + ", " + item);
        long externalcalls = System.nanoTime();
        itemResource.merge(item).run();
        totalexternaltime = totalexternaltime + System.nanoTime() - externalcalls;
        long duration = System.nanoTime() - startTime - totalexternaltime;
        HashMap logm = new HashMap();
        logm.put("runtime_ms",duration/1000);
        System.out.println("updateItem call took "+duration);
        span.log(logm);
        span.finish();       
    }
}
