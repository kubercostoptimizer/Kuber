NAME = sockshop_payment

.PHONY: default copy test

default: test

test:
	GROUP=khv129 COMMIT=test ./scripts/build.sh
	./test/test.sh unit.py
	./test/test.sh container.py --tag $(COMMIT)
