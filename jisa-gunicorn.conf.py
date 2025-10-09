import os

wsgi_app = os.getenv("APP_NAME", "src.app.app:app")
bind = os.getenv("HOST", "0.0.0.0") + ":" + os.getenv("PORT", "8000")
workers = int(os.getenv("WORKERS", "1"))
worker_class = os.getenv("UVICORN_WORKER", "uvicorn.workers.UvicornWorker")
loglevel = os.getenv("LOGLEVEL", "debug")
logconfig = os.getenv("LOGCONFIG", "./src/utils/logging.conf")
backlog = int(os.getenv("BACKLOG", "2048"))
max_requests = int(os.getenv("LIMIT_MAX_REQUESTS", "65536"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "2048"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "10"))
reload = False
