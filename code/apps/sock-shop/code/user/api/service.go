package api

// service.go contains the definition and implementation (business logic) of the
// user service. Everything here is agnostic to the transport (HTTP).

import (
	"crypto/sha1"
	"errors"
	"io"
	"time"
	"fmt"
	"context"
	"github.com/asystemsguy/user/db"
	"github.com/asystemsguy/user/users"
	opentracing "github.com/opentracing/opentracing-go"
)

var (
	ErrUnauthorized = errors.New("Unauthorized")
)

// Service is the user service, providing operations for users to login, register, and retrieve customer information.
type Service interface {
	Login(ctx context.Context,username, password string) (users.User, error) // GET /login
	Register(ctx context.Context,username, password, email, first, last string) (string, error)
	GetUsers(ctx context.Context,id string) ([]users.User, error)
	PostUser(ctx context.Context,u users.User) (string, error)
	GetAddresses(ctx context.Context,id string) ([]users.Address, error)
	PostAddress(ctx context.Context,u users.Address, userid string) (string, error)
	GetCards(ctx context.Context,id string) ([]users.Card, error)
	PostCard(ctx context.Context,u users.Card, userid string) (string, error)
	Delete(ctx context.Context,entity, id string) error
	Health() []Health // GET /health
}

// NewFixedService returns a simple implementation of the Service interface,
func NewFixedService() Service {
	return &fixedService{}
}

type fixedService struct{}

type Health struct {
	Service string `json:"service"`
	Status  string `json:"status"`
	Time    string `json:"time"`
}

func (s *fixedService) Login(ctx context.Context,username, password string) (users.User, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("Login")


	external_call_2 := time.Now()
	u, err := db.GetUserByName(username)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	if err != nil {
		return users.New(), err
	}
	if u.Password != calculatePassHash(password, u.Salt) {
		return users.New(), ErrUnauthorized
	}
	
	external_call_2 = time.Now()
	db.GetUserAttributes(&u)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	u.MaskCCs()
	
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return u, nil

}

func (s *fixedService) Register(ctx context.Context,username, password, email, first, last string) (string, error) {
	start := time.Now()

	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("Register")

	u := users.New()
	u.Username = username
	u.Password = calculatePassHash(password, u.Salt)
	u.Email = email
	u.FirstName = first
	u.LastName = last
	
	external_call_2 := time.Now()
	err := db.CreateUser(&u)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)


	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return u.UserID, err
}

func (s *fixedService) GetUsers(ctx context.Context,id string) ([]users.User, error) {
	start := time.Now()

	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("GetUsers")

	if id == "" {
		external_call_2 := time.Now()
		us, err := db.GetUsers()
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

		for k, u := range us {
			u.AddLinks()
			us[k] = u
		}
		return us, err
	}
	
	external_call_2 := time.Now()
	u, err := db.GetUser(id)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	u.AddLinks()
    fmt.Println([]users.User{u})

	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return []users.User{u}, err
}

func (s *fixedService) PostUser(ctx context.Context,u users.User) (string, error) {
	start := time.Now()

	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("PostUser")


	u.NewSalt()
	u.Password = calculatePassHash(u.Password, u.Salt)
	
	external_call_2 := time.Now()
	err := db.CreateUser(&u)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return u.UserID, err
}

func (s *fixedService) GetAddresses(ctx context.Context,id string) ([]users.Address, error) {
	start := time.Now()

	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("GetAddresses")

	if id == "" {
		external_call_2 := time.Now()
		as, err := db.GetAddresses()
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

		for k, a := range as {
			a.AddLinks()
			as[k] = a
		}
		return as, err
	}
	
	external_call_2 := time.Now()
	a, err := db.GetAddress(id)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	a.AddLinks()

	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return []users.Address{a}, err
}

func (s *fixedService) PostAddress(ctx context.Context,add users.Address, userid string) (string, error) {
	err := db.CreateAddress(&add, userid)
	return add.ID, err
}

func (s *fixedService) GetCards(ctx context.Context,id string) ([]users.Card, error) {
	start := time.Now()

	elapsed_external_call_time := time.Duration(0)
	tracer := opentracing.GlobalTracer()
	span := tracer.StartSpan("GetCards")

	if id == "" {
		
		external_call_2 := time.Now()
		cs, err := db.GetCards()
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

		for k, c := range cs {
			c.AddLinks()
			cs[k] = c
		}
		return cs, err
	}
	
	external_call_2 := time.Now()
	c, err := db.GetCard(id)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	c.AddLinks()
	
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return []users.Card{c}, err
}

func (s *fixedService) PostCard(ctx context.Context,card users.Card, userid string) (string, error) {
	err := db.CreateCard(&card, userid)
	return card.ID, err
}

func (s *fixedService) Delete(ctx context.Context,entity, id string) error {
	return db.Delete(entity, id)
}

func (s *fixedService) Health() []Health {
	var health []Health
	dbstatus := "OK"

	err := db.Ping()
	if err != nil {
		dbstatus = "err"
	}

	app := Health{"user", "OK", time.Now().String()}
	db := Health{"user-db", dbstatus, time.Now().String()}

	health = append(health, app)
	health = append(health, db)

	return health
}

func calculatePassHash(pass, salt string) string {
	h := sha1.New()
	io.WriteString(h, salt)
	io.WriteString(h, pass)
	return fmt.Sprintf("%x", h.Sum(nil))
}
