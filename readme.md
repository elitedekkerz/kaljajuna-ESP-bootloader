# Kaljajuna ESP bootloader

MQTT based bootloader for ESP8266 written in MircoPython. 

## Install
1. Clone project  
    'git clone https://github.com/elitedekkerz/beer-train-IPA'
2. Install python requirments  
    'pip3 install -r requirments.txt'
3. Update src/sys_config.py
    Set SSID and password for AP which to connect and IP for the MQTT broker
3. Download MicroPyhon  
    'wget -O upython.bin https://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin'
4. Flash MicroPython and copy python bootloader  
    './flash.sh /dev/ttyUSB0'

## Usage (Linux)
1. Install package 'mosquitto-clients'
2. Subscribe to all system messages (Change IP to MQTT brokes IP)

    mosquitto_sub -h 10.0.0.10 -t +/sys/# -v

    This will show all system messages from all devises that uses this bootloader.
    To get the UID of your device reboot it and keep track of connect topic 
    example '94b91400/sys/connect'. The first part in hex is the UID of the device.

    To get all messages only form this device subscribe to it with:

    mosquitto_sub -h 10.0.0.10 -t UID/# -v

3. Send commands to the bootloader
    - Identification LED on:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/led -m on

    - Identification LED off:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/led -m off

    - Toggle identification LED:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/led -m toggle

    - Select file to read/write:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/file -m file_name
            e.g. mosquitto_pub -h 10.0.0.10 -t UID/sys/file -m src/sys_config.py

    - Read file (Selected with file topic):

            mosquitto_pub -h 10.0.0.10 -t UID/sys/read -m ""

            File content is returned in topic UID/sys/resp

    - Write file (Selected with file topic):

            mosquitto_pub -h 10.0.0.10 -t UID/sys/write -m "text to the file"

            or directly from file:
            mosquitto_pub -h 10.0.0.10 -t UID/sys/write -f src/sys_config.py 

    - Reboot the device:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/reboot -m ""

    - Run the main application:

            mosquitto_pub -h 10.0.0.10 -t UID/sys/run -m ""

            This command will call function 'run()' from the app/main.py
     
4. Example
    - Write example app to the device with UID 94b91400:
    
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/file -m src/main.py
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/write -f example_app/main.py
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/reboot -m ""

            After reboot run:
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/run -m ""
    
    - Make the app run at boot:

            Change 'app_autorun' to True in sys_congfig.py

            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/file -m sys_config.py
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/write -f src/sys_config.py
            mosquitto_pub -h 10.0.0.10 -t 94b91400/sys/reboot -m ""
