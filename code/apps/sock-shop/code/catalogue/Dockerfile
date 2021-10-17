FROM golang:1.10

COPY . /go/src/github.com/asystemsguy/catalogue
WORKDIR /go/src/github.com/asystemsguy/catalogue

RUN go get -u github.com/FiloSottile/gvt
RUN gvt restore && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app github.com/asystemsguy/catalogue/cmd/cataloguesvc
CMD ["./app", "-port=8085"]
