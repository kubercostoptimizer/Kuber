mvn -DskipTests package
docker build . -t khv129/sockshop_shipping
docker push khv129/sockshop_shipping
