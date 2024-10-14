gunicorn -w 3 -b [::]:8080 auth_server:app 

# Wait for all background processes to complete
wait