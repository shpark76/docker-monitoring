# Monitoring Servers and Docker Containers using Prometheus with Grafana

## 1. Introduction
Infrastructure monitoring is the basis for application performance management. The underlying system’s availability and health must be maximized continually. To achieve this, one has to monitor the system metrics like CPU, memory, network, and disk. Response time lag, if any must be addressed swiftly. Here we'll take a look at how to Monitor servers (and even Docker Containers running inside the Server) using Grafana, Prometheus, Node Exporter, CAdvisor and Flask App.

![Prometheus overview](images/docker-prometheus-overview.png)

---

## 2. Core Components
- Grafana- Database for Analytics & monitoring solution
- Prometheus- Event monitoring and alerting
- Node-Exporter- Monitoring Linux host metrics
- CAdvisor- Monitoring metrics for the running Containers.
- Flask-App- Your Flask App (or Django, etc)

---

## 3. Running Docker Compose Up
```
$ docker-compose build

$ docker-compose up

Starting docker-monitoring_alertmanager_1  ... done
Starting docker-monitoring_node-exporter_1 ... done
Starting docker-monitoring_flask_app_1     ... done
...
Starting docker-monitoring_grafana_1       ... done
Attaching to docker-monitoring_alertmanager_1, docker-monitoring_flask_app_1, docker-monitoring_node-exporter_1, docker-monitoring_cadvisor_1, docker-monitoring_redis_1, 
....
alertmanager_1   | level=info ts=2021-01-10T02:35:10.540Z caller=cluster.go:161 component=cluster msg="setting advertise address explicitly" addr=172.24.0.2 port=9094
cadvisor_1       | W0110 02:35:10.890139       1 manager.go:349] Could not configure a source for OOM detection, disabling OOM events: open /dev/kmsg: no such file or directory
...
remote_addr=172.24.0.1 time_ms=0 size=49 referer="http://localhost:3001/d/_eX4mpl3/flask-app-dashboard?orgId=1&refresh=5s&from=now-15m&to=now"
flask_app_1      | 172.24.0.7 - - [10/Jan/2021 02:38:08] "GET /metrics HTTP/1.1" 200 -
flask_app_1      | 172.24.0.7 - - [10/Jan/2021 02:38:13] "GET /metrics HTTP/1.1" 200 -

```

---

## 4. Grafana UI
http://localhost:3001

Login with
id: admin
pw: 1234

### Docker container dashboard
![Docker container dashboard](images/docker-container-monitoring.png)

### Flask application dashboard
![Flask application dashboard](images/flask-app-monitoring.png)

---

## 5. Flask code

Metrics type: https://prometheus.io/docs/concepts/metric_types/

### requirements.txt
```
flask
redis
...
prometheus-flask-exporter
...
```

### Prometheus Flask exporter
This library provides HTTP request metrics to export into Prometheus. It can also track method invocations using convenient functions.

https://pypi.org/project/prometheus-flask-exporter/

### code:
![acode](images/flask-app-code.png)


## 6. How to configure a scrape on Prometheus
![How to configure a scrape on Prometheus](images/prometheus_scrape_flask_app.png)

### Note
> When you add a new source of scrape on Prometheus, you should validate the source of the metrics like cAdvisor, Java Spring API, Django, etc. If the validate of the srape is passed, you can wire into prometheus.yml. Here is how you can test it out with curl command.
> ``` 
> curl localhost:5000/metrics
> # HELP python_gc_objects_collected_total Objects collected during gc
> # TYPE python_gc_objects_collected_total counter
> python_gc_objects_collected_total{generation="0"} 1525.0
> python_gc_objects_collected_total{generation="1"} 33.0
> ...
> # HELP process_virtual_memory_bytes Virtual memory size in bytes.
> # TYPE process_virtual_memory_bytes gauge
> process_virtual_memory_bytes 1.91111168e+08
> # HELP process_resident_memory_bytes Resident memory size in bytes.
> # TYPE process_resident_memory_bytes gauge
> process_resident_memory_bytes 3.3411072e+07
> # HELP process_start_time_seconds Start time of the process since unix epoch in > seconds.
> flask_exporter_info{version="0.18.1"} 1.0
> # HELP flask_http_request_duration_seconds Flask HTTP request duration in seconds
> # TYPE flask_http_request_duration_seconds histogram
> # HELP flask_http_request_total Total number of HTTP requests
> # TYPE flask_http_request_total counter
> # HELP flask_http_request_exceptions_total Total number of HTTP requests which > resulted in an exception
> # TYPE flask_http_request_exceptions_total counter
> # HELP flask_app_info App Info, this can be anything you want
> # TYPE flask_app_info gauge
> ...
> flask_by_path_counter_total{path="/metrics"} 49.0
> # HELP flask_by_path_counter_created Request count by request paths
> # TYPE flask_by_path_counter_created gauge
> flask_by_path_counter_created{path="/metrics"} 1.6103074201825395e+09
> '''

---

## 7. Load simulation with Apache Benchmark
Apache benchmark is a simple-to-use tool to help you understand how an HTTP server copes with large volumes of traffic. https://httpd.apache.org/docs/2.4/programs/ab.html

i.e) Fire 500 requests, with a maximum concurrency of 10 at a time
```
$ ab -c 10 —n 500 —r localhost:5000
```

```
# Testing / path
$ ab -n 1000 -c 3 http://localhost:5000/
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        Werkzeug/1.0.1
Server Hostname:        localhost
Server Port:            5000

Document Path:          /
Document Length:        65 bytes

Concurrency Level:      3
Time taken for tests:   85.899 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      218000 bytes
HTML transferred:       65000 bytes
Requests per second:    11.64 [#/sec] (mean)
Time per request:       257.697 [ms] (mean)
Time per request:       85.899 [ms] (mean, across all concurrent requests)
Transfer rate:          2.48 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     4  257 143.3    259     504
Waiting:        4  257 143.3    258     504
Total:          4  257 143.3    259     504

Percentage of the requests served within a certain time (ms)
  50%    259
  66%    335
  75%    385
  80%    405
  90%    455
  95%    480
  98%    493
  99%    498
 100%    504 (longest request)



# Testing /abc path
$ ab -n 1000 -c 3 http://localhost:5000/abc
...

# Testing /foo path
$ ab -n 1000 -c 3 http://localhost:5000/foo
...

```

#### Note) alternative GUI tool: With JMeter
> JMeter is a more powerful tool than Apache Benchmark and allows you to be a bit more specific about 
> how your traffic is fired. For example, with JMeter it is possible to say “Send 1000 requests spaced > out over 1 minute”, which is much more realistic. It is so configurable that it provides a GUI 
> (Graphical User Interface) to help you set up your tests. https://jmeter.apache.org/

---

## 8. Folder structure
```
├── README.md
├── alertmanager
│   └── config.yml
├── docker-compose.yml
├── flask
│   ├── Dockerfile
│   ├── api
│   │   ├── server.py
│   │   └── wsgi.py
│   └── requirements.txt
├── grafana
│   ├── config.monitoring
│   └── provisioning
│       ├── dashboards
│       │   ├── Docker\ Prometheus\ Monitoring-1571332751387.json
│       │   ├── FlaskApp_Monitoring.json
│       │   └── dashboard.yml
│       └── datasources
│           └── datasource.yml
└── prometheus
    ├── alert.rules
    └── prometheus.yml

8 directories, 14 files
```

---

## Reference:
- Prometheus: https://prometheus.io
- Prometheus Flask Package: https://github.com/rycus86/prometheus_flask_exporter
- CAdvisor(System resource montoring): https://github.com/google/cadvisor
- Apache HTTP server benchmarking tool: https://httpd.apache.org/docs/2.4/programs/ab.html