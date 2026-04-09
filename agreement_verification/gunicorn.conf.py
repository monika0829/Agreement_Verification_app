import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
reload = False

accesslog = "/var/log/supervisor/service-bg-service-1.log"
errorlog = "/var/log/supervisor/service-bg-service-1.log"
loglevel = "info"
