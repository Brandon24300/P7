#!/bin/bash
# source venv/bin/activate
# Start the api server
#cd api && python -m api &
cd api && gunicorn -b localhost:5000 api:app &


port=${PORT:-8050}
echo "port value $port"
sleep 15
# Start the dashboard server
#cd dashboard && python -m dashboard &
cd dashboard && gunicorn -b 0.0.0.0:"$port"  dashboard:server &

wait -n

# Exit with status of process that exited first
exit $?