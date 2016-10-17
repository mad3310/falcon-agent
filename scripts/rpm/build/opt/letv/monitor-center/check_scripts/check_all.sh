timeout 1m curl "http://127.0.0.1:8000/alarms/query/57/mysql" &
timeout 1m curl "http://127.0.0.1:8000/alarms/query/80/mysql" &
wait
