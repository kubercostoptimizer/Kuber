package frontend

import (
	"encoding/json"
	"fmt"
	"github.com/harlow/go-micro-services/services/recommendation/proto"
	"github.com/harlow/go-micro-services/services/reservation/proto"
	"github.com/harlow/go-micro-services/services/user/proto"
	"net/http"
	"time"
	"strconv"
	"github.com/harlow/go-micro-services/dialer"
	"github.com/harlow/go-micro-services/services/profile/proto"
	"github.com/harlow/go-micro-services/services/search/proto"
	// "github.com/harlow/go-micro-services/tracing"
	"github.com/opentracing/opentracing-go"
)

// Server implements frontend service
type Server struct {
	searchClient         search.SearchClient
	profileClient        profile.ProfileClient
	recommendationClient recommendation.RecommendationClient
	userClient           user.UserClient
	reservationClient    reservation.ReservationClient
	IpAddr	 string
	Port     int
	Tracer   opentracing.Tracer
}

// Run the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	if err := s.initSearchClient("search"); err != nil {
		return err
	}

	if err := s.initProfileClient("profile"); err != nil {
		return err
	}

	if err := s.initRecommendationClient("recommendation"); err != nil {
		return err
	}

	if err := s.initUserClient("user"); err != nil {
		return err
	}

	if err := s.initReservation("reservation"); err != nil {
		return err
	}

	// fmt.Printf("frontend before mux\n")

	mux := http.NewServeMux()
	mux.Handle("/", http.FileServer(http.Dir("services/frontend/static")))
	mux.Handle("/hotels", http.HandlerFunc(s.searchHandler))
	mux.Handle("/recommendations", http.HandlerFunc(s.recommendHandler))
	mux.Handle("/user", http.HandlerFunc(s.userHandler))
	mux.Handle("/reservation", http.HandlerFunc(s.reservationHandler))

    fmt.Printf("frontend starts serving\n")

	return http.ListenAndServe(fmt.Sprintf(":%d", s.Port), mux)
}

func (s *Server) initSearchClient(name string) error {
	conn, err := dialer.Dial("search:8082")
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.searchClient = search.NewSearchClient(conn)
	return nil
}

func (s *Server) initProfileClient(name string) error {
	conn, err := dialer.Dial("profile:8081")
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.profileClient = profile.NewProfileClient(conn)
	return nil
}

func (s *Server) initRecommendationClient(name string) error {
	conn, err := dialer.Dial("recommendation:8085")
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.recommendationClient = recommendation.NewRecommendationClient(conn)
	return nil
}

func (s *Server) initUserClient(name string) error {
	conn, err := dialer.Dial("user:8086")
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.userClient = user.NewUserClient(conn)
	return nil
}

func (s *Server) initReservation(name string) error {
	conn, err := dialer.Dial("reservation:8087")
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.reservationClient = reservation.NewReservationClient(conn)
	return nil
}

func (s *Server) searchHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	searchHandlertrace := s.Tracer.StartSpan("searchHandler")
	
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()


    fmt.Printf("starts searchHandler\n")

	// in/out dates from query params
	inDate, outDate := r.URL.Query().Get("inDate"), r.URL.Query().Get("outDate")
	if inDate == "" || outDate == "" {
		http.Error(w, "Please specify inDate/outDate params", http.StatusBadRequest)
		return
	}

	// lan/lon from query params
	sLat, sLon := r.URL.Query().Get("lat"), r.URL.Query().Get("lon")
	if sLat == "" || sLon == "" {
		http.Error(w, "Please specify location params", http.StatusBadRequest)
		return
	}

	Lat, _ := strconv.ParseFloat(sLat, 32)
	lat := float32(Lat)
	Lon, _ := strconv.ParseFloat(sLon, 32)
	lon := float32(Lon)

	fmt.Printf("starts searchHandler querying downstream\n")

	// search for best hotels
	// nearbysp := s.Tracer.StartSpan("External_call_to_Nearby", opentracing.ChildOf(searchHandlertrace.Context()))
	external_call_1 := time.Now()
	searchResp, err := s.searchClient.Nearby(ctx, &search.NearbyRequest{
		Lat:     lat,
		Lon:     lon,
		InDate:  inDate,
		OutDate: outDate,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)
	// nearbysp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// fmt.Printf("searchHandler gets searchResp\n")
	// for _, hid := range searchResp.HotelIds {
	// 	fmt.Printf("search Handler hotelId = %s\n", hid)
	// }

	// grab locale from query params or default to en
	locale := r.URL.Query().Get("locale")
	if locale == "" {
		locale = "en"
	}

	// reservationRespsp := s.Tracer.StartSpan("External_call_CheckAvailability", opentracing.ChildOf(searchHandlertrace.Context()))
	external_call_2 := time.Now()
	reservationResp, err := s.reservationClient.CheckAvailability(ctx, &reservation.Request{
		CustomerName: "",
		HotelId:      searchResp.HotelIds,
		InDate:       inDate,
		OutDate:      outDate,
		RoomNumber:   1,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	// reservationRespsp.Finish()

	// fmt.Printf("searchHandler gets reserveResp\n")
	// fmt.Printf("searchHandler gets reserveResp.HotelId = %s\n", reservationResp.HotelId)

	// hotel profiles
	// profileRespsp := s.Tracer.StartSpan("External_call_GetProfiles", opentracing.ChildOf(searchHandlertrace.Context()))
	external_call_3 := time.Now()
	profileResp, err := s.profileClient.GetProfiles(ctx, &profile.Request{
		HotelIds: reservationResp.HotelId,
		Locale:   locale,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_3)

	// profileRespsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// fmt.Printf("searchHandler gets profileResp\n")

	json.NewEncoder(w).Encode(geoJSONResponse(profileResp.Hotels))
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	searchHandlertrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	searchHandlertrace.Finish()
}

func (s *Server) recommendHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	recommendHandlertrace := s.Tracer.StartSpan("recommendHandler")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()


	sLat, sLon := r.URL.Query().Get("lat"), r.URL.Query().Get("lon")
	if sLat == "" || sLon == "" {
		http.Error(w, "Please specify location params", http.StatusBadRequest)
		return
	}
	Lat, _ := strconv.ParseFloat(sLat, 64)
	lat := float64(Lat)
	Lon, _ := strconv.ParseFloat(sLon, 64)
	lon := float64(Lon)

	require := r.URL.Query().Get("require")
	if require != "dis" && require != "rate" && require != "price" {
		http.Error(w, "Please specify require params", http.StatusBadRequest)
		return
	}

	// recommendationClientsp := s.Tracer.StartSpan("External_call_GetRecommendations", opentracing.ChildOf(recommendHandlertrace.Context()))
	// recommend hotels
	external_call_1 := time.Now()
	recResp, err := s.recommendationClient.GetRecommendations(ctx, &recommendation.Request{
		Require: require,
		Lat:     float64(lat),
		Lon:     float64(lon),
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)
	// recommendationClientsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// grab locale from query params or default to en
	locale := r.URL.Query().Get("locale")
	if locale == "" {
		locale = "en"
	}

	// profileClientsp := s.Tracer.StartSpan("External_call_GetProfiles", opentracing.ChildOf(recommendHandlertrace.Context()))
	// hotel profiles
	external_call_2 := time.Now()
	profileResp, err := s.profileClient.GetProfiles(ctx, &profile.Request{
		HotelIds: recResp.HotelIds,
		Locale:   locale,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)
	// profileClientsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(geoJSONResponse(profileResp.Hotels))
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	recommendHandlertrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	recommendHandlertrace.Finish()
}

func (s *Server) userHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	userHandlertrace := s.Tracer.StartSpan("userHandler")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	username, password := r.URL.Query().Get("username"), r.URL.Query().Get("password")
	if username == "" || password == "" {
		http.Error(w, "Please specify username and password", http.StatusBadRequest)
		return
	}

	// userClientsp := s.Tracer.StartSpan("External_call_CheckUser", opentracing.ChildOf(userHandlertrace.Context()))
	// Check username and password
	external_call_1 := time.Now()
	recResp, err := s.userClient.CheckUser(ctx, &user.Request{
		Username: username,
		Password: password,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)

	// userClientsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	str := "Login successfully!"
	if recResp.Correct == false {
		str = "Failed. Please check your username and password. "
	}

	res := map[string]interface{}{
		"message": str,
	}

	json.NewEncoder(w).Encode(res)
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	userHandlertrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	userHandlertrace.Finish()
}

func (s *Server) reservationHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	elapsed_external_call_time := time.Duration(0)
	reservationHandlertrace := s.Tracer.StartSpan("reservationHandler")

	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	inDate, outDate := r.URL.Query().Get("inDate"), r.URL.Query().Get("outDate")
	if inDate == "" || outDate == "" {
		http.Error(w, "Please specify inDate/outDate params", http.StatusBadRequest)
		return
	}

	if !checkDataFormat(inDate) || !checkDataFormat(outDate) {
		http.Error(w, "Please check inDate/outDate format (YYYY-MM-DD)", http.StatusBadRequest)
		return
	}

	hotelId := r.URL.Query().Get("hotelId")
	if hotelId == "" {
		http.Error(w, "Please specify hotelId params", http.StatusBadRequest)
		return
	}

	customerName := r.URL.Query().Get("customerName")
	if customerName == "" {
		http.Error(w, "Please specify customerName params", http.StatusBadRequest)
		return
	}

	username, password := r.URL.Query().Get("username"), r.URL.Query().Get("password")
	if username == "" || password == "" {
		http.Error(w, "Please specify username and password", http.StatusBadRequest)
		return
	}

	numberOfRoom := 0
	num := r.URL.Query().Get("number")
	if num != "" {
		numberOfRoom, _ = strconv.Atoi(num)
	}

	// userClientsp := s.Tracer.StartSpan("External_call_CheckUser", opentracing.ChildOf(reservationHandlertrace.Context()))
	// Check username and password
	external_call_1 := time.Now()
	recResp, err := s.userClient.CheckUser(ctx, &user.Request{
		Username: username,
		Password: password,
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_1)

	// userClientsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	str := "Reserve successfully!"
	if recResp.Correct == false {
		str = "Failed. Please check your username and password. "
	}

	// reservationClientsp := s.Tracer.StartSpan("External_call_MakeReservation", opentracing.ChildOf(reservationHandlertrace.Context()))
	// Make reservation
	external_call_2 := time.Now()

	resResp, err := s.reservationClient.MakeReservation(ctx, &reservation.Request{
		CustomerName: customerName,
		HotelId:      []string{hotelId},
		InDate:       inDate,
		OutDate:      outDate,
		RoomNumber:   int32(numberOfRoom),
	})
	elapsed_external_call_time = elapsed_external_call_time + time.Since(external_call_2)

	// reservationClientsp.Finish()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if len(resResp.HotelId) == 0 {
		str = "Failed. Already reserved. "
	}

	res := map[string]interface{}{
		"message": str,
	}

	json.NewEncoder(w).Encode(res)
	elapsed := time.Since(start)
	elapsed = elapsed - elapsed_external_call_time
	reservationHandlertrace.LogKV("runtime_ms",float64(elapsed)/float64(time.Millisecond))
	reservationHandlertrace.Finish()
}

// return a geoJSON response that allows google map to plot points directly on map
// https://developers.google.com/maps/documentation/javascript/datalayer#sample_geojson
func geoJSONResponse(hs []*profile.Hotel) map[string]interface{} {
	fs := []interface{}{}

	for _, h := range hs {
		fs = append(fs, map[string]interface{}{
			"type": "Feature",
			"id":   h.Id,
			"properties": map[string]string{
				"name":         h.Name,
				"phone_number": h.PhoneNumber,
			},
			"geometry": map[string]interface{}{
				"type": "Point",
				"coordinates": []float32{
					h.Address.Lon,
					h.Address.Lat,
				},
			},
		})
	}

	return map[string]interface{}{
		"type":     "FeatureCollection",
		"features": fs,
	}
}

func checkDataFormat(date string) bool {
	if len(date) != 10 {
		return false
	}
	for i := 0; i < 10; i++ {
		if i == 4 || i == 7 {
			if date[i] != '-' {
				return false
			}
		} else {
			if date[i] < '0' || date[i] > '9' {
				return false
			}
		}
	}
	return true
}