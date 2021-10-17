mvn -DskipTests package
docker build . -t khv129/sockshop_orders
docker push khv129/sockshop_orders

