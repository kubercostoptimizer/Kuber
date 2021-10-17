FROM golang:1.10

COPY . /go/src/github.com/asystemsguy/payment
WORKDIR /go/src/github.com/asystemsguy/payment

RUN go get -u github.com/FiloSottile/gvt
RUN gvt restore 
RUN go build -a -installsuffix cgo -o app github.com/asystemsguy/payment/cmd/paymentsvc
RUN ls -l
CMD ["./app", "-port=8084"]

#EXPOSE 80
