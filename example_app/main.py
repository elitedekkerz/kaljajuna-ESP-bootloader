import utime
import machine

mqtt = None

def pin_callback():
    #Publish message "down" in topic "down"
    global mqtt
    mqtt.pub("pin", "down")

def hello_callback(message):
    #Print "hello" and message when we receive 
    print("hello {}".format(message))

def run(mqtt_obj, parameters):
    #Make mqtt object global, so it can be called from interrupts
    global mqtt 
    mqtt = mqtt_obj
    
    #Set project name as prefix so we can easily filter topics
    #Final topic will be in form:
    #UID/prefix/user_topic
    mqtt.set_prefix("example")

    #Subscribe to topic "hello"
    mqtt.sub("hello", hello_callback)

    #Setup callback for pin 0
    p0 = machine.Pin(0, machine.Pin.IN)
    p0.irq(trigger=machine.Pin.IRQ_FALLING, handler=pin_callback)

    #Main loop
    i = 0
    while True:
        #Call periodicaly to check if we have recived new messages. 
        mqtt.check_msg()

        #Publish to counter
        mqtt.pub("counter", i)
        i += 1

        #Do all the things (or sleep)

        utime.sleep(5)