#!/bin/bash

# Start Gunicorn for the calculation server on port 5001 with 3 workers
gunicorn -w 3 -b [::]:5000 calc_server:app &

# Wait for all background processes to complete
wait
