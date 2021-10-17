package reservation

import (
	// "encoding/json"
	"fmt"
	// "github.com/grpc-ecosystem/grpc-opentracing/go/otgrpc"
	// "github.com/harlow/go-micro-services/registry"
	pb "github.com/harlow/go-micro-services/services/reservation/proto"
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

	"github.com/bradfitz/gomemcache/memcache"
	// "strings"
	"strconv"
)

const name = "reservation"

// Server implements the user service
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

	pb.RegisterReservationServer(srv, s)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	fmt.Printf("In reservation s.IpAddr = %s, port = %d\n", s.IpAddr, s.Port)

	return srv.Serve(lis)
}

// MakeReservation makes a reservation based on given information
func (s *Server) MakeReservation(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	MakeReservationtrace := s.Tracer.StartSpan("MakeReservation")

	res := new(pb.Result)
	res.HotelId = make([]string, 0)

	// session, err := mgo.Dial("mongodb-reservation")
	// if err != nil {
	// 	panic(err)
	// }
	session := s.MongoSession.Copy()
	defer session.Close()

	c := session.DB("reservation-db").C("reservation")
	c1 := session.DB("reservation-db").C("number")

	inDate, _ := time.Parse(
		time.RFC3339,
		req.InDate + "T12:00:00+00:00")

	outDate, _ := time.Parse(
		time.RFC3339,
		req.OutDate + "T12:00:00+00:00")
	hotelId := req.HotelId[0]

	indate := inDate.String()[0:10]

	memc_date_num_map := make(map[string] int)

	for inDate.Before(outDate) {
		// check reservations
		count := 0
		inDate = inDate.AddDate(0, 0, 1)
		outdate := inDate.String()[0:10]

		// first check memc
		memc_key := hotelId + "_" + inDate.String()[0:10] + "_" + outdate

		// memcached1sp := s.Tracer.StartSpan("External_call_to_memcached1_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
		external_call_1 := time.Now()
		item, err := s.MemcClient.Get(memc_key)
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)

		// memcached1sp.Finish()
			
		if err == nil {
			// memcached hit
			count, _ = strconv.Atoi(string(item.Value))
			fmt.Printf("memcached hit %s = %d\n", memc_key, count)
			memc_date_num_map[memc_key] = count + int(req.RoomNumber)

		} else if err == memcache.ErrCacheMiss {
			// memcached miss
			// fmt.Printf("memcached miss\n")
			reserve := make([]reservation, 0)
			
			// mango1sp := s.Tracer.StartSpan("External_call_to_mango1_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
			external_call_2 := time.Now()
			err := c.Find(&bson.M{"hotelId": hotelId, "inDate": indate, "outDate": outdate}).All(&reserve)
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
			// mango1sp.Finish()

			if err != nil {
				panic(err)
			}
			
			for _, r := range reserve {
				count += r.Number
			}

			memc_date_num_map[memc_key] = count + int(req.RoomNumber)

		} else {
			fmt.Printf("Memmcached error = %s\n", err)
			panic(err)
		}
		
		// check capacity
		// check memc capacity
		memc_cap_key := hotelId + "_cap"
		// memcached2sp := s.Tracer.StartSpan("External_call_to_memcached2_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
		external_call_3 := time.Now()
		item, err = s.MemcClient.Get(memc_cap_key)
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_3)
	
		// memcached2sp.Finish()

		hotel_cap := 0
		if err == nil {
			// memcached hit
			hotel_cap, _ = strconv.Atoi(string(item.Value))
			fmt.Printf("memcached hit %s = %d\n", memc_cap_key, hotel_cap)
		} else if err == memcache.ErrCacheMiss {
			// memcached miss
			var num number
			
			// mango2sp := s.Tracer.StartSpan("External_call_to_mango2_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
			external_call_4 := time.Now()
			err = c1.Find(&bson.M{"hotelId": hotelId}).One(&num)
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_4)
			// mango2sp.Finish()

			if err != nil {
				panic(err)
			}
			hotel_cap = int(num.Number)

			// write to memcache
			// memcached3sp := s.Tracer.StartSpan("External_call_to_memcached3_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
			external_call_5 := time.Now()
			s.MemcClient.Set(&memcache.Item{Key: memc_cap_key, Value: []byte(strconv.Itoa(hotel_cap))})
			// memcached3sp.Finish()
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_5)

		} else {
			fmt.Printf("Memmcached error = %s\n", err)
			panic(err)
		}

		if count + int(req.RoomNumber) > hotel_cap {
			return res, nil
		}
		indate = outdate
	}

	// only update reservation number cache after check succeeds
	for key, val := range memc_date_num_map {
		// memcached4sp := s.Tracer.StartSpan("External_call_to_memcached4_reservation", opentracing.ChildOf(MakeReservationtrace.Context()))
		external_call_6 := time.Now()
		s.MemcClient.Set(&memcache.Item{Key: key, Value: []byte(strconv.Itoa(val))})
		elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_6)
		// memcached4sp.Finish()
	}

	inDate, _ = time.Parse(
		time.RFC3339,
		req.InDate + "T12:00:00+00:00")

	indate = inDate.String()[0:10]

	for inDate.Before(outDate) {
		inDate = inDate.AddDate(0, 0, 1)
		outdate := inDate.String()[0:10]
		err := c.Insert(&reservation{
			HotelId:      hotelId,
			CustomerName: req.CustomerName,
			InDate:       indate,
			OutDate:      outdate,
			Number:       int(req.RoomNumber),})
		if err != nil {
			panic(err)
		}
		indate = outdate
	}

	res.HotelId = append(res.HotelId, hotelId)

	fmt.Printf("end MakeReservation\n");
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	MakeReservationtrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	MakeReservationtrace.Finish()
	return res, nil
}

// CheckAvailability checks if given information is available
func (s *Server) CheckAvailability(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	CheckAvailabilitytrace := s.Tracer.StartSpan("CheckAvailability")

	fmt.Printf("calling CheckAvailability\n");
	res := new(pb.Result)
	res.HotelId = make([]string, 0)

	session := s.MongoSession.Copy()
	defer session.Close()

	c := session.DB("reservation-db").C("reservation")
	c1 := session.DB("reservation-db").C("number")

	for _, hotelId := range req.HotelId {
		fmt.Printf("reservation check hotel %s\n", hotelId)
		inDate, _ := time.Parse(
			time.RFC3339,
			req.InDate + "T12:00:00+00:00")

		outDate, _ := time.Parse(
			time.RFC3339,
			req.OutDate + "T12:00:00+00:00")

		indate := inDate.String()[0:10]

		for inDate.Before(outDate) {
			// check reservations
			count := 0
			inDate = inDate.AddDate(0, 0, 1)
			fmt.Printf("reservation check date %s\n", inDate.String()[0:10])
			outdate := inDate.String()[0:10]

			// first check memc
			memc_key := hotelId + "_" + inDate.String()[0:10] + "_" + outdate

			external_call_1 := time.Now()
			// memcachedsp := s.Tracer.StartSpan("External_call_to_memcached_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
			item, err := s.MemcClient.Get(memc_key)
			// memcachedsp.Finish()
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)

			if err == nil {
				// memcached hit
				count, _ = strconv.Atoi(string(item.Value))
				fmt.Printf("memcached hit %s = %d\n", memc_key, count)
			} else if err == memcache.ErrCacheMiss {
				// memcached miss
				reserve := make([]reservation, 0)
			
				external_call_2 := time.Now()
				// mongodbsp := s.Tracer.StartSpan("External_call_to_mangodb_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
				err := c.Find(&bson.M{"hotelId": hotelId, "inDate": indate, "outDate": outdate}).All(&reserve)
				// mongodbsp.Finish()
				elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
					
				if err != nil {
					panic(err)
				}
				for _, r := range reserve {
					fmt.Printf("reservation check reservation number = %d\n", hotelId)
					count += r.Number
				}

				// update memcached
				external_call_3 := time.Now()
				// memcachedwsp := s.Tracer.StartSpan("External_call_to_memcachedw_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
				s.MemcClient.Set(&memcache.Item{Key: memc_key, Value: []byte(strconv.Itoa(count))})
				// memcachedwsp.Finish()
				elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_3)

			} else {
				fmt.Printf("Memmcached error = %s\n", err)
				panic(err)
			}

			// check capacity
			// check memc capacity
			memc_cap_key := hotelId + "_cap"

			external_call_4 := time.Now()
			// memcachedw2sp := s.Tracer.StartSpan("External_call_to_memcachedw2_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
			item, err = s.MemcClient.Get(memc_cap_key)
			// memcachedw2sp.Finish()
			elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_4)

			hotel_cap := 0

			if err == nil {
				// memcached hit
				hotel_cap, _ = strconv.Atoi(string(item.Value))
				fmt.Printf("memcached hit %s = %d\n", memc_cap_key, hotel_cap)
			} else if err == memcache.ErrCacheMiss { 
				var num number

				external_call_5 := time.Now()
				// mongodb2sp := s.Tracer.StartSpan("External_call_to_mangodb2_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
				err = c1.Find(&bson.M{"hotelId": hotelId}).One(&num)
				// mongodb2sp.Finish()
				elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_5)
					
				if err != nil {
					panic(err)
				}
				hotel_cap = int(num.Number)
				// update memcached
				external_call_6 := time.Now()
				// memcachedw3sp := s.Tracer.StartSpan("External_call_to_memcachedw3_reservation", opentracing.ChildOf(CheckAvailabilitytrace.Context()))
				s.MemcClient.Set(&memcache.Item{Key: memc_cap_key, Value: []byte(strconv.Itoa(hotel_cap))})
				// memcachedw3sp.Finish()
				elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_6)

			} else {
				fmt.Printf("Memmcached error = %s\n", err)
				panic(err)
			}

			if count + int(req.RoomNumber) > hotel_cap {
				break
			}
			indate = outdate

			if inDate.Equal(outDate) {
				res.HotelId = append(res.HotelId, hotelId)
			}
		}
	}
	fmt.Printf("end CheckAvailability\n");
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	CheckAvailabilitytrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	CheckAvailabilitytrace.Finish()
	return res, nil
}

type reservation struct {
	HotelId      string `bson:"hotelId"`
	CustomerName string `bson:"customerName"`
	InDate       string `bson:"inDate"`
	OutDate      string `bson:"outDate"`
	Number       int    `bson:"number"`
}

type number struct {
	HotelId      string `bson:"hotelId"`
	Number       int    `bson:"numberOfRoom"`
}
