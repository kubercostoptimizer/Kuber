package main

import (
	"flag"
	"fmt"
	"os"
	"os/signal"
	//"strings"
	"syscall"

	"github.com/go-kit/kit/log"
	opentracing "github.com/opentracing/opentracing-go"
	metrics     "github.com/uber/jaeger-lib/metrics"
        jaeger      "github.com/uber/jaeger-client-go"
        jaegercfg   "github.com/uber/jaeger-client-go/config"
        jaegerlog   "github.com/uber/jaeger-client-go/log"

	//"net"
	"net/http"

	"path/filepath"

	_ "github.com/go-sql-driver/mysql"
	"github.com/jmoiron/sqlx"
	"github.com/asystemsguy/catalogue"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/weaveworks/common/middleware"
	"golang.org/x/net/context"
)

const (
	ServiceName = "catalogue"
)

var (
	HTTPLatency = prometheus.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "http_request_duration_seconds",
		Help:    "Time (in seconds) spent serving HTTP requests.",
		Buckets: prometheus.DefBuckets,
	}, []string{"method", "path", "status_code", "isWS"})
)

func init() {
	prometheus.MustRegister(HTTPLatency)
}

func main() {
	var (
		port   = flag.String("port", "80", "Port to bind HTTP listener") // TODO(pb): should be -addr, default ":80"
		images = flag.String("images", "./images/", "Image path")
		dsn    = flag.String("DSN", "catalogue_user:default_password@tcp(catalogue-db:3306)/socksdb", "Data Source Name: [username[:password]@][protocol[(address)]]/dbname")
	)
	flag.Parse()

	fmt.Fprintf(os.Stderr, "images: %q\n", *images)
	abs, err := filepath.Abs(*images)
	fmt.Fprintf(os.Stderr, "Abs(images): %q (%v)\n", abs, err)
	pwd, err := os.Getwd()
	fmt.Fprintf(os.Stderr, "Getwd: %q (%v)\n", pwd, err)
	files, _ := filepath.Glob(*images + "/*")
	fmt.Fprintf(os.Stderr, "ls: %q\n", files) // contains a list of all files in the current directory

	// Mechanical stuff.
	errc := make(chan error)
	ctx := context.Background()

	// Log domain.
	var logger log.Logger
	{
		logger = log.NewLogfmtLogger(os.Stderr)
		logger = log.NewContext(logger).With("ts", log.DefaultTimestampUTC)
		logger = log.NewContext(logger).With("caller", log.DefaultCaller)
	}

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
	    tracer,_,_ := cfg.NewTracer(
		jaegercfg.Logger(jLogger),
		jaegercfg.Metrics(jMetricsFactory),
	    )
	    // Set the singleton opentracing.Tracer with the Jaeger tracer.
	    opentracing.SetGlobalTracer(tracer)

	// Data domain.
	db, err := sqlx.Open("mysql", *dsn)
	if err != nil {
		logger.Log("err", err)
		os.Exit(1)
	}
	defer db.Close()

	// Check if DB connection can be made, only for logging purposes, should not fail/exit
	err = db.Ping()
	if err != nil {
		logger.Log("Error", "Unable to connect to Database", "DSN", dsn)
	}

	// Service domain.
	var service catalogue.Service
	{
		service = catalogue.NewCatalogueService(db, logger)
		service = catalogue.LoggingMiddleware(logger)(service)
	}

	// Endpoint domain.
	endpoints := catalogue.MakeEndpoints(service, tracer)

	// HTTP router
	router := catalogue.MakeHTTPHandler(ctx, endpoints, *images, logger, tracer)

	httpMiddleware := []middleware.Interface{
		middleware.Instrument{
			Duration:     HTTPLatency,
			RouteMatcher: router,
		},
	}

	// Handler
	handler := middleware.Merge(httpMiddleware...).Wrap(router)

	// Create and launch the HTTP server.
	go func() {
		logger.Log("transport", "HTTP", "port", *port)
		errc <- http.ListenAndServe(":"+*port, handler)
	}()

	// Capture interrupts.
	go func() {
		c := make(chan os.Signal)
		signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
		errc <- fmt.Errorf("%s", <-c)
	}()

	logger.Log("exit", <-errc)
}
