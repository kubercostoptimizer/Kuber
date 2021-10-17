package catalogue

// service.go contains the definition and implementation (business logic) of the
// catalogue service. Everything here is agnostic to the transport (HTTP).

import (
	"errors"
	"strings"
	"time"
	"context"
	"github.com/opentracing/opentracing-go"
	"github.com/go-kit/kit/log"
	"github.com/jmoiron/sqlx"
)

// Service is the catalogue service, providing read operations on a saleable
// catalogue of sock products.
type Service interface {
	List(ctx context.Context,tags []string, order string, pageNum, pageSize int) ([]Sock, error) // GET /catalogue
	Count(ctx context.Context,tags []string) (int, error)                                        // GET /catalogue/size
	Get(ctx context.Context,id string) (Sock, error)                                             // GET /catalogue/{id}
	Tags() ([]string, error)                                                 // GET /tags
	Health() []Health                                                        // GET /health
}

// Middleware decorates a Service.
type Middleware func(Service) Service

// Sock describes the thing on offer in the catalogue.
type Sock struct {
	ID          string   `json:"id" db:"id"`
	Name        string   `json:"name" db:"name"`
	Description string   `json:"description" db:"description"`
	ImageURL    []string `json:"imageUrl" db:"-"`
	ImageURL_1  string   `json:"-" db:"image_url_1"`
	ImageURL_2  string   `json:"-" db:"image_url_2"`
	Price       float32  `json:"price" db:"price"`
	Count       int      `json:"count" db:"count"`
	Tags        []string `json:"tag" db:"-"`
	TagString   string   `json:"-" db:"tag_name"`
}

// Health describes the health of a service
type Health struct {
	Service string `json:"service"`
	Status  string `json:"status"`
	Time    string `json:"time"`
}

// ErrNotFound is returned when there is no sock for a given ID.
var ErrNotFound = errors.New("not found")

// ErrDBConnection is returned when connection with the database fails.
var ErrDBConnection = errors.New("database connection error")

var baseQuery = "SELECT sock.sock_id AS id, sock.name, sock.description, sock.price, sock.count, sock.image_url_1, sock.image_url_2, GROUP_CONCAT(tag.name) AS tag_name FROM sock JOIN sock_tag ON sock.sock_id=sock_tag.sock_id JOIN tag ON sock_tag.tag_id=tag.tag_id"

// NewCatalogueService returns an implementation of the Service interface,
// with connection to an SQL database.
func NewCatalogueService(db *sqlx.DB, logger log.Logger) Service {
	return &catalogueService{
		db:     db,
		logger: logger,
	}
}

type catalogueService struct {
	db     *sqlx.DB
	logger log.Logger
}

func (s *catalogueService) List(ctx context.Context,tags []string, order string, pageNum, pageSize int) ([]Sock, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	span := opentracing.StartSpan("List")

	var socks []Sock
	query := baseQuery

	var args []interface{}

	for i, t := range tags {
		if i == 0 {
			query += " WHERE tag.name=?"
			args = append(args, t)
		} else {
			query += " OR tag.name=?"
			args = append(args, t)
		}
	}

	query += " GROUP BY id"

	if order != "" {
		query += " ORDER BY ?"
		args = append(args, order)
	}

	query += ";"

	external_call_2 := time.Now()
	err := s.db.Select(&socks, query, args...)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	
	if err != nil {
		s.logger.Log("database error", err)
		return []Sock{}, ErrDBConnection
	}
	for i, s := range socks {
		socks[i].ImageURL = []string{s.ImageURL_1, s.ImageURL_2}
		socks[i].Tags = strings.Split(s.TagString, ",")
	}

	// DEMO: Change 0 to 850
	time.Sleep(0 * time.Millisecond)

	socks = cut(socks, pageNum, pageSize)

	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return socks, nil
}

func (s *catalogueService) Count(ctx context.Context,tags []string) (int, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)

	span := opentracing.StartSpan("Count")


	query := "SELECT COUNT(DISTINCT sock.sock_id) FROM sock JOIN sock_tag ON sock.sock_id=sock_tag.sock_id JOIN tag ON sock_tag.tag_id=tag.tag_id"

	var args []interface{}

	for i, t := range tags {
		if i == 0 {
			query += " WHERE tag.name=?"
			args = append(args, t)
		} else {
			query += " OR tag.name=?"
			args = append(args, t)
		}
	}

	query += ";"

	external_call_2 := time.Now()
	sel, err := s.db.Prepare(query)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	
	if err != nil {
		s.logger.Log("database error", err)
		return 0, ErrDBConnection
	}
	defer sel.Close()

	var count int

    external_call_2 = time.Now()
	err = sel.QueryRow(args...).Scan(&count)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	
	if err != nil {
		s.logger.Log("database error", err)
		return 0, ErrDBConnection
	}

	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	
	return count, nil
}

func (s *catalogueService) Get(ctx context.Context,id string) (Sock, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)

	span := opentracing.StartSpan("Get")
	
	query := baseQuery + " WHERE sock.sock_id =? GROUP BY sock.sock_id;"

	var sock Sock
	
	external_call_2 := time.Now()
	err := s.db.Get(&sock, query, id)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	
	if err != nil {
		s.logger.Log("database error", err)
		return Sock{}, ErrNotFound
	}

	sock.ImageURL = []string{sock.ImageURL_1, sock.ImageURL_2}
	sock.Tags = strings.Split(sock.TagString, ",")
	
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return sock, nil
}

func (s *catalogueService) Health() []Health {

	var health []Health
	dbstatus := "OK"

	err := s.db.Ping()
	if err != nil {
		dbstatus = "err"
	}
	
	app := Health{"catalogue", "OK", time.Now().String()}
	db := Health{"catalogue-db", dbstatus, time.Now().String()}

	health = append(health, app)
	health = append(health, db)


	return health
}

func (s *catalogueService) Tags() ([]string, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)

	span := opentracing.StartSpan("Tags")
	var tags []string
	query := "SELECT name FROM tag;"

	external_call_2 := time.Now()
	rows, err := s.db.Query(query)
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	
	if err != nil {
		s.logger.Log("database error", err)
		return []string{}, ErrDBConnection
	}
	var tag string
	for rows.Next() {
		err = rows.Scan(&tag)
		if err != nil {
			s.logger.Log("database error", err)
			continue
		}
		tags = append(tags, tag)
	}
	
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	span.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	span.Finish()
	return tags, nil
}

func cut(socks []Sock, pageNum, pageSize int) []Sock {
	if pageNum == 0 || pageSize == 0 {
		return []Sock{} // pageNum is 1-indexed
	}
	start := (pageNum * pageSize) - pageSize
	if start > len(socks) {
		return []Sock{}
	}
	end := (pageNum * pageSize)
	if end > len(socks) {
		end = len(socks)
	}
	return socks[start:end]
}

func contains(s []string, e string) bool {
	for _, a := range s {
		if a == e {
			return true
		}
	}
	return false
}
