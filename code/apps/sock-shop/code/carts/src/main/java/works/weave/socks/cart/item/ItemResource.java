package works.weave.socks.cart.item;

import io.opentracing.Scope;
import io.jaegertracing.Configuration;

import works.weave.socks.cart.cart.Resource;
import works.weave.socks.cart.entities.Item;

import java.util.function.Supplier;

public class ItemResource implements Resource<Item> {
    private final ItemDAO itemRepository;
    private final Supplier<Item> item;

    public ItemResource(ItemDAO itemRepository, Supplier<Item> item) {
        this.itemRepository = itemRepository;
        this.item = item;
    }

    @Override
    public Runnable destroy() {
            Runnable obj = () -> itemRepository.destroy(value().get());
            return obj;
    }

    @Override
    public Supplier<Item> create() {
            Supplier<Item> obj = () -> itemRepository.save(item.get());
            return obj;
    }

    @Override
    public Supplier<Item> value() {
        return item;    // Basically a null method. Gets the item from the supplier.
    }

    @Override
    public Runnable merge(Item toMerge) {
        Runnable obj = () -> itemRepository.save(new Item(value().get(), toMerge.quantity()));
        return obj;
    }
}
