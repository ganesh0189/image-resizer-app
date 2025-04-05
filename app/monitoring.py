from prometheus_client import Counter, Histogram, Gauge
from flask import request
import time
import statsd

# Initialize StatsD client
statsd_client = statsd.StatsClient(host='localhost', port=8125, prefix='image_resizer')

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

UPLOAD_SIZE = Histogram(
    'upload_size_bytes',
    'Size of uploaded files in bytes'
)

def start_timer():
    request.start_time = time.time()

def stop_timer(response):
    resp_time = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(resp_time)
    return response

def record_request_data(response):
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

def setup_metrics(app):
    app.before_request(start_timer)
    app.after_request(record_request_data)
    app.after_request(stop_timer)

def record_upload_size(size_bytes):
    UPLOAD_SIZE.observe(size_bytes)
    statsd_client.gauge('upload.size', size_bytes)

def increment_active_users():
    ACTIVE_USERS.inc()
    statsd_client.incr('users.active')

def decrement_active_users():
    ACTIVE_USERS.dec()
    statsd_client.decr('users.active') 