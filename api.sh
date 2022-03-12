#!/bin/bash
# source venv/bin/activate
# Start the api server
port=${PORT:-8050}
cd api && gunicorn -b 0.0.0.0:"$port"  api:app &

wait -n

# Exit with status of process that exited first
exit $?