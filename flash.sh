
PORT=$1

echo $PORT

esptool.py --port $PORT erase_flash
esptool.py --port $PORT --baud 460800 write_flash --flash_size=detect 0 upython.bin
sleep 2
ampy -p $PORT put src/main.py main.py
ampy -p $PORT put src/mqtt_wrap.py mqtt_wrap.py
ampy -p $PORT put src/sys_config.py sys_config.py

echo "DONE"