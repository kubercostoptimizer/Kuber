package main

import (
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"github.com/asystemsguy/payment"
	"golang.org/x/net/context"
	opentracing "github.com/opentracing/opentracing-go"
	metrics     "github.com/uber/jaeger-lib/metrics"
        jaeger      "github.com/uber/jaeger-client-go"
        jaegercfg   "github.com/uber/jaeger-client-go/config"
        jaegerlog   "github.com/uber/jaeger-client-go/log"
)

const (
	ServiceName = "payment"
)

func main() {
	var (
		port          = flag.String("port", "8080", "Port to bind HTTP listener")
		declineAmount = flag.Float64("decline", 105, "Decline payments over certain amount")
	)
	flag.Parse()
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
		/*
	var tracer stdopentracing.Tracer
	{
		// Log domain.
		var logger log.Logger
		{
			logger = log.NewLogfmtLogger(os.Stderr)
			logger = log.NewContext(logger).With("ts", log.DefaultTimestampUTC)
			logger = log.NewContext(logger).With("caller", log.DefaultCaller)
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
		if *zip == "" {
			tracer = stdopentracing.NoopTracer{}
		} else {
			logger := log.NewContext(logger).With("tracer", "Zipkin")
			logger.Log("addr", zip)
			collector, err := zipkin.NewHTTPCollector(
				*zip,
				zipkin.HTTPLogger(logger),
			)
			if err != nil {
				logger.Log("err", err)
				os.Exit(1)
			}
			tracer, err = zipkin.NewTracer(
				zipkin.NewRecorder(collector, false, fmt.Sprintf("%v:%v", host, port), ServiceName),
			)
			if err != nil {
				logger.Log("err", err)
				os.Exit(1)
			}
		}
		stdopentracing.InitGlobalTracer(tracer)

	}
       */
	// Mechanical stuff.
	errc := make(chan error)
	ctx := context.Background()

	handler, logger := payment.WireUp(ctx, float32(*declineAmount), tracer, ServiceName)

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
