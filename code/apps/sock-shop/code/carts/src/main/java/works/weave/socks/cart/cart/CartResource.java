package works.weave.socks.cart.cart;

import io.opentracing.Scope;
import io.jaegertracing.Configuration;

import works.weave.socks.cart.action.FirstResultOrDefault;
import works.weave.socks.cart.entities.Cart;

import java.util.function.Supplier;

public class CartResource implements Resource<Cart>, HasContents<CartContentsResource> {
    private final CartDAO cartRepository;
    private final String customerId;

    public CartResource(CartDAO cartRepository, String customerId) {
        this.cartRepository = cartRepository;
        this.customerId = customerId;
    }

    @Override
    public Runnable destroy() {
            Runnable obj = () -> cartRepository.delete(value().get());
            return obj;
    }

    @Override
    public Supplier<Cart> create() {
            Supplier<Cart> obj = () -> cartRepository.save(new Cart(customerId));
            return obj;
    }

    @Override
    public Supplier<Cart> value() {
            Supplier<Cart> obj = new FirstResultOrDefault<>(
                    cartRepository.findByCustomerId(customerId),
                    () -> {
                        create().get();
                        return value().get();
                    });

            return obj;
    }

    @Override
    public Runnable merge(Cart toMerge) {
            Runnable obj = () -> toMerge.contents().forEach(item -> contents().get().add(() -> item).run());
            return obj;
    }

    @Override
    public Supplier<CartContentsResource> contents() {
            Supplier<CartContentsResource> obj = () -> new CartContentsResource(cartRepository, () -> this);
            return obj;
    }
}
