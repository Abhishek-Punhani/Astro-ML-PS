#!/bin/bash

# Start Gunicorn for the calculation server on port 5001 with 3 workers
gunicorn -w 3 -b localhost:5001 calc_server:app &

# Start Gunicorn for the calculation server on port 5002 with 3 workers
gunicorn -w 3 -b localhost:5002 calc_server:app &

# Start Gunicorn for the calculation server on port 5003 with 3 workers
gunicorn -w 3 -b localhost:5003 calc_server:app &

# Start the authentication server on port 4000 (adjust the port as needed)
gunicorn -w 3 -b localhost:8080 auth_server:app &

# Wait for all background processes to complete
wait
