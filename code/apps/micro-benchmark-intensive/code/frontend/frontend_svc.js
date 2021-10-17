var express = require('express')
const fetch = require("node-fetch");
var app = express();

const request = require('request');

var initTracer = require('jaeger-client').initTracer;


var config = {
     serviceName: 'frontend',
     reporter: {
          'agentHost': 'jaeger-agent.istio-system.svc.cluster.local',
          'logspans': true
     },
     sampler: {
          type: 'const',
          param: 1.0
     }
};

options = {}

var tracer = initTracer(config, options);

process.on('exit', () => {
     console.log('flush out remaining span')
     tracer.close()
})

//handle ctrl+c
process.on('SIGINT', () => {
     process.exit()
})

async function getAllUrls(urls) {
     try {
         var data = await Promise.all(
             urls.map(
                 url =>
                     fetch(url).then(
                         (response) => response.json()
                     )));
 
         return (data)
 
     } catch (error) {
         console.log(error)
 
         throw (error)
     }
 }

let urls = ['http://comservice1:8080/run','http://comservice2:8080/run','http://comservice3:8080/run','http://comservice4:8080/run','http://comservice5:8080/run' ]

app.get('/run', async function(req, res) {
     
     try {
     const traceSpan = tracer.startSpan('run')
     var start = new Date()
     
     var responses = await getAllUrls(urls) 
     
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
     // res.sendStatus(200);
     // console.log("run")
})

var server = app.listen(8081, function () {
     
     var host = server.address().address
     var port = server.address().port
     console.log("APP is running on http://%s:%s", host, port)
})
