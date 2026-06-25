# Use gevent instead of --threaded, as the latter requires an exact number of active SSE sessions
# Single worker to match what we did with Flask, and also to keep any in-memory data in sync
# Timeout for SSE since we heartbeat anyway
# Put access and error logs to stdout, so that pm2 or screen or whatever will show it
gunicorn -k gevent --timeout 120 --access-logfile - --error-logfile - -b 0.0.0.0:4646 main:app $@
