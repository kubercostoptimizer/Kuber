package user

import (
	"crypto/sha256"
	// "encoding/json"
	"fmt"
	// "github.com/grpc-ecosystem/grpc-opentracing/go/otgrpc"
	pb "github.com/harlow/go-micro-services/services/user/proto"
	"github.com/opentracing/opentracing-go"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	// "io/ioutil"
	"log"
	"net"
	// "os"
	"time"
)

const name = "user"

// Server implements the user service
type Server struct {
	users map[string]string

	Tracer   opentracing.Tracer
	Port     int
	IpAddr	 string
	MongoSession 	*mgo.Session
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	if s.users == nil {
		s.users = loadUsers(s.MongoSession)
	}

	srv := grpc.NewServer(
		grpc.KeepaliveParams(keepalive.ServerParameters{
			Timeout: 120 * time.Second,
		}),
		grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
			PermitWithoutStream: true,
		}),
		// grpc.UnaryInterceptor(
		// 	otgrpc.OpenTracingServerInterceptor(s.Tracer),
		// ),
	)

	pb.RegisterUserServer(srv, s)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	return srv.Serve(lis)
}

// // Shutdown cleans up any processes
// func (s *Server) Shutdown() {
// 	s.Registry.Deregister(name)
// }

// CheckUser returns whether the username and password are correct.
func (s *Server) CheckUser(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	CheckUsertrace := s.Tracer.StartSpan("CheckUser")
	res := new(pb.Result)

	fmt.Printf("CheckUser")

	sum := sha256.Sum256([]byte(req.Password))
	pass := fmt.Sprintf("%x", sum)

	res.Correct = false
	if true_pass, found := s.users[req.Username]; found {
	    res.Correct = pass == true_pass
	}
	
	fmt.Printf("CheckUser %d\n", res.Correct)
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	CheckUsertrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	CheckUsertrace.Finish()
	return res, nil
}

// loadUsers loads hotel users from mongodb.
func loadUsers(session *mgo.Session) map[string]string {
	// session, err := mgo.Dial("mongodb-user")
	// if err != nil {
	// 	panic(err)
	// }
	// defer session.Close()
	s := session.Copy()
	defer s.Close()
	c := s.DB("user-db").C("user")

	// unmarshal json profiles
	var users []User
	err := c.Find(bson.M{}).All(&users)
	if err != nil {
		log.Println("Failed get users data: ", err)
	}

	res := make(map[string]string)
	for _, user := range users {
		res[user.Username] = user.Password
	}

	fmt.Printf("Done load users\n")

	return res
}

type User struct {
	Username string `bson:"username"`
	Password string `bson:"password"`
}