package tracing

import (
	"fmt"
	opentracing "github.com/opentracing/opentracing-go"
	"github.com/uber/jaeger-client-go/config"
)

// Init returns a newly configured tracer
func Init(serviceName, host string) (opentracing.Tracer, error) {
	cfg := config.Configuration{
		Sampler: &config.SamplerConfig{
			Type:  "const",
			Param: 1,
		},
		Reporter: &config.ReporterConfig{
			LogSpans:            true,
			LocalAgentHostPort:  host,
		},
	}

	tracer, _, err := cfg.New(serviceName)
	if err != nil {
		return nil, fmt.Errorf("new tracer error: %v", err)
	}
	return tracer, nil
}
