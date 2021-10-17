FROM golang:1.10

ENV HATEAOS user
ENV USER_DATABASE mongodb
ENV MONGO_HOST user-db

ENV sourcesdir /go/src/github.com/asystemsguy/user/
ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN apt-get update && apt-get install -yq git curl
RUN curl https://glide.sh/get | sh

COPY . ${sourcesdir}
WORKDIR ${sourcesdir}
RUN glide install
RUN go build main.go
CMD ["./main", "-port=8086"]

#EXPOSE 80
