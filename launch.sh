#!/bin/bash
# source venv/bin/activate
# Start the api server
cd api && python -m api &


sleep 10
# Start the dashboard server
cd dashboard && python -m dashboard &