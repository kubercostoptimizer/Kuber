var express = require('express')

var app = express();

var initTracer = require('jaeger-client').initTracer;

var config = {
     serviceName: 'comservice5',
     sampler: {
          type: "const",
          param: 1,
     },
     reporter: {
          agentHost: 'jaeger-agent.istio-system.svc.cluster.local',
          logSpans: true
     },
};

options = {}

process.on('exit', () => {
     console.log('flush out remaining span')
     tracer.close()
})

//handle ctrl+c
process.on('SIGINT', () => {
     process.exit()
})

app.get('/run', function(req, res) {
     try {
     var tracer = initTracer(config, options);
     console.log('got a request on /run')
     const traceSpan = tracer.startSpan('run')
     var start = new Date()
     var x = 0 
     for (var i=0; i< 2000000000; i++) {
         x = x + 2
         x = x * 2
     } 
     var duration = new Date() - start

     res.status(200).json(duration);
     traceSpan.log({'runtime_ms': duration});
     traceSpan.finish();
     tracer.close()
     } catch(e) {
          console.log(e);
          res.status(200);
          tracer.close()
     }
})

var server = app.listen(8081, function () {
     var host = server.address().address
     var port = server.address().port
     process.env.UV_THREADPOOL_SIZE = 8
     console.log('LIBUV Threads: ', process.env.UV_THREADPOOL_SIZE);
     console.log("APP is running on http://%s:%s", host, port)
})
