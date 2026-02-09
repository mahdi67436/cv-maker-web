"""
FreeUltraCV Gunicorn Configuration
===================================
Production WSGI server configuration.
"""

import os
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "freultracv"

# Server mechanics
daemon = False
pidfile = "/var/run/freultracv/gunicorn.pid"
user = "www-data"
group = "www-data"
umask = 0
tmp_upload_dir = None

# Logging
errorlog = "/var/log/freultracv/error.log"
accesslog = "/var/log/freultracv/access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process management
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 50

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment
raw_env = [
    'FLASK_ENV=production',
    'SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO, https',
]

# Preload app for better memory usage
preload_app = True

def on_starting(server):
    """Called just before master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during reload."""
    pass

def worker_int(worker):
    """Called when worker receives INT or QUIT signal."""
    pass

def worker_abort(worker):
    """Called when worker receives SIGABRT signal."""
    pass
