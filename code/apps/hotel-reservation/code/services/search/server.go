package search

import (
	// "encoding/json"
	"fmt"
	// F"io/ioutil"
	"log"
	"net"
	// "os"
	"time"

	// "github.com/grpc-ecosystem/grpc-opentracing/go/otgrpc"
	"github.com/harlow/go-micro-services/dialer"
	// "github.com/harlow/go-micro-services/registry"
	geo "github.com/harlow/go-micro-services/services/geo/proto"
	rate "github.com/harlow/go-micro-services/services/rate/proto"
	pb "github.com/harlow/go-micro-services/services/search/proto"
	opentracing "github.com/opentracing/opentracing-go"
	context "golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
)

const name = "search"

// Server implments the search service
type Server struct {
	geoClient  geo.GeoClient
	rateClient rate.RateClient

	Tracer   opentracing.Tracer
	Port     int
	IpAddr	 string
	// Registry *registry.Client
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
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
	pb.RegisterSearchServer(srv, s)

	// init grpc clients
	if err := s.initGeoClient("geo"); err != nil {
		return err
	}
	if err := s.initRateClient("rate"); err != nil {
		return err
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// register with consul
	// jsonFile, err := os.Open("config.json")
	// if err != nil {
	// 	fmt.Println(err)
	// }

	// defer jsonFile.Close()

	// byteValue, _ := ioutil.ReadAll(jsonFile)

	// var result map[string]string
	// json.Unmarshal([]byte(byteValue), &result)

    fmt.Printf("In search s.IpAddr = %s, port = %d\n", s.IpAddr, s.Port)

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

func (s *Server) initGeoClient(name string) error {
	conn, err := dialer.Dial(
		"geo:8083",
		
		// dialer.WithBalancer(s.Registry.Client),
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.geoClient = geo.NewGeoClient(conn)
	return nil
}

func (s *Server) initRateClient(name string) error {
	conn, err := dialer.Dial(
		"rate:8084",
		// dialer.WithBalancer(s.Registry.Client),
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.rateClient = rate.NewRateClient(conn)
	return nil
}

// Nearby returns ids of nearby hotels ordered by ranking algo
func (s *Server) Nearby(ctx context.Context, req *pb.NearbyRequest) (*pb.SearchResult, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	Nearbytrace := s.Tracer.StartSpan("Nearby")

	// find nearby hotels
	fmt.Printf("in Search Nearby\n")

	fmt.Printf("nearby lat = %f\n", req.Lat)
	fmt.Printf("nearby lon = %f\n", req.Lon)

	// Nearbysp := s.Tracer.StartSpan("External_call_to_Nearby", opentracing.ChildOf(Nearbytrace.Context()))
	external_call_1 := time.Now()
	nearby, err := s.geoClient.Nearby(ctx, &geo.Request{
		Lat: req.Lat,
		Lon: req.Lon,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)
	// Nearbysp.Finish()

	if err != nil {
		log.Fatalf("nearby error: %v", err)
	}

	for _, hid := range nearby.HotelIds {
		fmt.Printf("get Nearby hotelId = %s\n", hid)
	}

	// GetRatessp := s.Tracer.StartSpan("External_call_to_GetRates", opentracing.ChildOf(Nearbytrace.Context()))
	// find rates for hotels
	external_call_2 := time.Now()
	rates, err := s.rateClient.GetRates(ctx, &rate.Request{
		HotelIds: nearby.HotelIds,
		InDate:   req.InDate,
		OutDate:  req.OutDate,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	// GetRatessp.Finish()

	if err != nil {
		log.Fatalf("rates error: %v", err)
	}

	// TODO(hw): add simple ranking algo to order hotel ids:
	// * geo distance
	// * price (best discount?)
	// * reviews

	// build the response
	res := new(pb.SearchResult)
	for _, ratePlan := range rates.RatePlans {
		fmt.Printf("get RatePlan HotelId = %s, Code = %s\n", ratePlan.HotelId, ratePlan.Code)
		res.HotelIds = append(res.HotelIds, ratePlan.HotelId)
	}
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	Nearbytrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	Nearbytrace.Finish()
	return res, nil
}
