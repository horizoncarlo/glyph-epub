# Use gevent instead of --threaded, as the latter requires an exact number of active SSE sessions
# Workers 2 to match our VPS
# Timeout for SSE since we heartbeat anyway
# Put access and error logs to stdout, so that pm2 or screen or whatever will show it
# Then usual binding to port and running the app
gunicorn -k gevent --workers 2 --timeout 120 --access-logfile - --error-logfile - --log-level debug -b 0.0.0.0:4646 main:app
