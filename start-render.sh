#!/bin/bash
set -e
redis-server --loadmodule /var/lib/falkordb/bin/falkordb.so THREAD_COUNT 2 --bind 127.0.0.1 --port 6379 --daemonize yes --dir /tmp --pidfile /tmp/recallgraph-redis.pid
for n in $(seq 1 30); do
  if redis-cli ping >/dev/null 2>&1; then break; fi
  sleep 1
done
/opt/venv/bin/python -c 'from memory import Memory; Memory().reset()'
exec /opt/venv/bin/gunicorn --bind "0.0.0.0:${PORT:-8080}" --workers 1 --threads 4 app:app
