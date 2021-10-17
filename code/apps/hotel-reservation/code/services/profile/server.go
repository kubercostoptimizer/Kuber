package profile

import (
	"encoding/json"
	"fmt"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	// "io/ioutil"
	"log"
	"net"
	// "os"
	"time"

	// "github.com/grpc-ecosystem/grpc-opentracing/go/otgrpc"
	// "github.com/harlow/go-micro-services/registry"
	pb "github.com/harlow/go-micro-services/services/profile/proto"
	"github.com/opentracing/opentracing-go"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"

	"github.com/bradfitz/gomemcache/memcache"
	// "strings"
)

const name = "profile"

// Server implements the profile service
type Server struct {
	Tracer   opentracing.Tracer
	Port     int
	IpAddr	 string
	MongoSession	*mgo.Session
	// Registry *registry.Client
	MemcClient *memcache.Client
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	fmt.Printf("in run s.IpAddr = %s, port = %d\n", s.IpAddr, s.Port)

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

	pb.RegisterProfileServer(srv, s)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// register the service
	// jsonFile, err := os.Open("config.json")
	// if err != nil {
	// 	fmt.Println(err)
	// }

	// defer jsonFile.Close()

	// byteValue, _ := ioutil.ReadAll(jsonFile)

	// var result map[string]string
	// json.Unmarshal([]byte(byteValue), &result)

	// err = s.Registry.Register(name, s.IpAddr, s.Port)
	// if err != nil {
	// 	return fmt.Errorf("failed register: %v", err)
	// }

	return srv.Serve(lis)
}

// // Shutdown cleans up any processes
// func (s *Server) Shutdown() {
// 	s.Registry.Deregister(name)
// }

// GetProfiles returns hotel profiles for requested IDs
func (s *Server) GetProfiles(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	GetProfilestrace := s.Tracer.StartSpan("GetProfiles")

	// session, err := mgo.Dial("mongodb-profile")
	// if err != nil {
	// 	panic(err)
	// }
	// defer session.Close()
	fmt.Printf("In GetProfiles\n")

	fmt.Printf("In GetProfiles after setting c\n")

	res := new(pb.Result)
	hotels := make([]*pb.Hotel, 0)

	// one hotel should only have one profile

	for _, i := range req.HotelIds {
		// first check memcached
		// memcached1sp := s.Tracer.StartSpan("External_call_to_memcached1_profile", opentracing.ChildOf(GetProfilestrace.Context()))
		external_call_1 := time.Now()
		item, err := s.MemcClient.Get(i)
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)
		// memcached1sp.Finish()

		if err == nil {
			// memcached hit
			profile_str := string(item.Value)

			fmt.Printf("memc hit\n")
			fmt.Println(profile_str)

			hotel_prof := new(pb.Hotel)
			json.Unmarshal(item.Value, hotel_prof)
			hotels = append(hotels, hotel_prof)

		} else if err == memcache.ErrCacheMiss {
			// memcached miss, set up mongo connection
			session := s.MongoSession.Copy()
			defer session.Close()
			c := session.DB("profile-db").C("hotels")

			hotel_prof := new(pb.Hotel)
			// mango1sp := s.Tracer.StartSpan("External_call_to_mango1_profile", opentracing.ChildOf(GetProfilestrace.Context()))
			external_call_2 := time.Now()
			err := c.Find(bson.M{"id": i}).One(&hotel_prof)
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

			// mango1sp.Finish()

			if err != nil {
				log.Println("Failed get hotels data: ", err)
			}

			// for _, h := range hotels {
			// 	res.Hotels = append(res.Hotels, h)
			// }
			hotels = append(hotels, hotel_prof)

			prof_json, err := json.Marshal(hotel_prof)
			memc_str := string(prof_json)

			// write to memcached
			// memcached2sp := s.Tracer.StartSpan("External_call_to_memcached2_profile", opentracing.ChildOf(GetProfilestrace.Context()))
			external_call_3 := time.Now()
			s.MemcClient.Set(&memcache.Item{Key: i, Value: []byte(memc_str)})
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_3)

			// memcached2sp.Finish()

		} else {
			fmt.Printf("Memmcached error = %s\n", err)
			panic(err)
		}
	}

	res.Hotels = hotels
	fmt.Printf("In GetProfiles after getting resp\n")
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	GetProfilestrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	GetProfilestrace.Finish()
	return res, nil
}
