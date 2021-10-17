package payment

import (
	"errors"
	"fmt"
	"time"
	"context"
	"github.com/opentracing/opentracing-go"
)

// Middleware decorates a service.
type Middleware func(Service) Service

type Service interface {
	Authorise(ctx context.Context, total float32) (Authorisation, error) // GET /paymentAuth
	Health() []Health                               // GET /health
}

type Authorisation struct {
	Authorised bool   `json:"authorised"`
	Message    string `json:"message"`
}

type Health struct {
	Service string `json:"service"`
	Status  string `json:"status"`
	Time    string `json:"time"`
}

// NewFixedService returns a simple implementation of the Service interface,
// fixed over a predefined set of socks and tags. In a real service you'd
// probably construct this with a database handle to your socks DB, etc.
func NewAuthorisationService(declineOverAmount float32) Service {
	return &service{
		declineOverAmount: declineOverAmount,
	}
}

type service struct {
	declineOverAmount float32
}

func (s *service) Authorise(ctx context.Context, amount float32) (Authorisation, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	span := opentracing.StartSpan("Authorise")

	if amount == 0 {
		return Authorisation{}, ErrInvalidPaymentAmount
	}
	if amount < 0 {
		return Authorisation{}, ErrInvalidPaymentAmount
	}
	authorised := false
	message := "Payment declined"
	if amount <= s.declineOverAmount {
		authorised = true
		message = "Payment authorised"
	} else {
		message = fmt.Sprintf("Payment declined: amount exceeds %.2f", s.declineOverAmount)
	}
	
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()

	return Authorisation{
		Authorised: authorised,
		Message:    message,
	}, nil
}

func (s *service) Health() []Health {
	var health []Health
	app := Health{"payment", "OK", time.Now().String()}
	health = append(health, app)
	return health
}

var ErrInvalidPaymentAmount = errors.New("Invalid payment amount")
