FROM golang:1.10

COPY . /go/src/github.com/harlow/go-micro-services
WORKDIR /go/src/github.com/harlow/go-micro-services
RUN go get gopkg.in/mgo.v2
RUN go get github.com/bradfitz/gomemcache/memcache
RUN go get github.com/uber/jaeger-client-go/
RUN go get github.com/pkg/errors
RUN go get github.com/opentracing/opentracing-go
RUN go get github.com/grpc-ecosystem/grpc-opentracing/go/otgrpc
RUN go get github.com/opentracing-contrib/go-stdlib/nethttp
RUN go install -ldflags="-s -w" ./cmd/...
