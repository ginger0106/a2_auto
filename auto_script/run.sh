kill -9 `lsof -t -i:9000`
echo "kill 9000..."
kill -9 `lsof -t -i:20020`
echo "kill 20020..." 
killall python
echo "kill python"
nohup python a2_auto/auto_script/auto_server.py &

