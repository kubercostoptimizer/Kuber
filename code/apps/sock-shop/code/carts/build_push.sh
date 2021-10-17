mvn -DskipTests package
docker build . -t khv129/sockshop_carts
docker push khv129/sockshop_carts
#kubectl delete -f carts.yaml
#kubectl create -f carts.yaml
