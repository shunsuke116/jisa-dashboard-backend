@echo off

set HOST=0.0.0.0
set PORT=8000
set WORKERS=1
set LOGLEVEL=debug
set LOGCONFIG=./src/utils/logging.conf
set BACKLOG=2048
set LIMIT_MAX_REQUESTS=65536
set APP_NAME=src.app.app:app

uvicorn ${APP_NAME} ^
--host ${HOST} ^
--port ${PORT} ^
--workers ${WORKERS} ^
--log-level ${LOGLEVEL} ^
--log-config ${LOGCONFIG} ^
--backlog ${BACKLOG} ^
--limit-max-requests ${LIMIT_MAX_REQUESTS}
