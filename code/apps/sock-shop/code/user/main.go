package main

import (
	"flag"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	corelog "log"
	"github.com/go-kit/kit/log"
	kitprometheus "github.com/go-kit/kit/metrics/prometheus"
	"github.com/asystemsguy/user/api"
	"github.com/asystemsguy/user/db"
	"github.com/asystemsguy/user/db/mongodb"
	opentracing "github.com/opentracing/opentracing-go"
	metrics     "github.com/uber/jaeger-lib/metrics"
	jaeger      "github.com/uber/jaeger-client-go"
	jaegercfg   "github.com/uber/jaeger-client-go/config"
	jaegerlog   "github.com/uber/jaeger-client-go/log"
	stdprometheus "github.com/prometheus/client_golang/prometheus"
	commonMiddleware "github.com/weaveworks/common/middleware"
)

var (
	port string
)

var (
	HTTPLatency = stdprometheus.NewHistogramVec(stdprometheus.HistogramOpts{
		Name:    "http_request_duration_seconds",
		Help:    "Time (in seconds) spent serving HTTP requests.",
		Buckets: stdprometheus.DefBuckets,
	}, []string{"method", "path", "status_code", "isWS"})
)

const (
	ServiceName = "user"
)

func init() {
	stdprometheus.MustRegister(HTTPLatency)
	flag.StringVar(&port, "port", "8084", "Port on which to run")
	db.Register("mongodb", &mongodb.Mongo{})
}

func main() {

	flag.Parse()
	// Mechanical stuff.
	errc := make(chan error)

	// Log domain.
	var logger log.Logger
	{
		logger = log.NewLogfmtLogger(os.Stderr)
		logger = log.With(logger, "ts", log.DefaultTimestampUTC)
		logger = log.With(logger, "caller", log.DefaultCaller)
	}

	// Find service local IP.
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		logger.Log("err", err)
		os.Exit(1)
	}
	localAddr := conn.LocalAddr().(*net.UDPAddr)
	host := strings.Split(localAddr.String(), ":")[0]
	defer conn.Close()

	// Sample configuration for testing. Use constant sampling to sample every trace
	// and enable LogSpan to log every span via configured Logger.
	cfg := jaegercfg.Configuration{
		ServiceName: ServiceName,
	Sampler:     &jaegercfg.SamplerConfig{
		Type:  jaeger.SamplerTypeConst,
		Param: 1,
	},
	Reporter:    &jaegercfg.ReporterConfig{
		LocalAgentHostPort: "jaeger-agent.istio-system.svc.cluster.local:6831",
		LogSpans: true,
	},
	}

	// Example logger and metrics factory. Use github.com/uber/jaeger-client-go/log
	// and github.com/uber/jaeger-lib/metrics respectively to bind to real logging and metrics
	// frameworks.
	jLogger := jaegerlog.StdLogger
	jMetricsFactory := metrics.NullFactory

	// Initialize tracer with a logger and a metrics factory
	tracer,closer,_ := cfg.NewTracer(
	jaegercfg.Logger(jLogger),
	jaegercfg.Metrics(jMetricsFactory),
	)
	// Set the singleton opentracing.Tracer with the Jaeger tracer.
	opentracing.SetGlobalTracer(tracer)
	defer closer.close()

	dbconn := false
	for !dbconn {
		err := db.Init()
		if err != nil {
			if err == db.ErrNoDatabaseSelected {
				corelog.Fatal(err)
			}
			corelog.Print(err)
		} else {
			dbconn = true
		}
	}

	fieldKeys := []string{"method"}
	// Service domain.
	var service api.Service
	
	// Endpoint domain.
	endpoints := api.MakeEndpoints(service, tracer)

	// HTTP router
	router := api.MakeHTTPHandler(endpoints, logger, tracer)

	httpMiddleware := []commonMiddleware.Interface{
		commonMiddleware.Instrument{
			Duration:     HTTPLatency,
			RouteMatcher: router,
		},
	}

	// Handler
	handler := commonMiddleware.Merge(httpMiddleware...).Wrap(router)

	// Create and launch the HTTP server.
	go func() {
		logger.Log("transport", "HTTP", "port", port)
		errc <- http.ListenAndServe(fmt.Sprintf(":%v", port), handler)
	}()

	// Capture interrupts.
	go func() {
		c := make(chan os.Signal)
		signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
		errc <- fmt.Errorf("%s", <-c)
	}()

	logger.Log("exit", <-errc)
}
