import time
import ubinascii
import machine
import sys_config
import ure
from umqtt.simple import MQTTClient

class mqtt_wrap():
    def __init__(self, prefix="undef"):
        uid = ubinascii.hexlify(machine.unique_id())
        self._uid = uid.decode("utf8")
        self._prefix = prefix
        self._mqtt = MQTTClient(uid, sys_config.mqtt_broker)
        self._mqtt.connect()
        self._mqtt.set_callback(self._callback_func)
        self._callbacks = {}
        print("Connected")

    def check_msg(self):
        self._new_msg = True
        while self._new_msg:
            self._new_msg = False
            self._mqtt.check_msg()

    def pub(self, topic, message, prefix=None):
        prefix = self._prefix if prefix is None else prefix
        topic = "/".join((self._uid, prefix, topic))

        print("pub: {} -> {}".format(topic, str(message)))
        self._mqtt.publish(topic, str(message))

    def sub(self, topic, callback, prefix=None):
        prefix = self._prefix if prefix is None else prefix
        topic = "/".join((self._uid, prefix, topic))   

        print("sub: {}".format(topic))
        self._callbacks.update({topic: callback})
        self._mqtt.subscribe(topic)

    def set_prefix(self, prefix):
        self._prefix = prefix

    def _callback_func(self, topic, message):
        self._new_msg = True
        topic = topic.decode("utf8")
        message = message.decode("utf8")
        print("recv: {} -> {}".format(topic, str(message)))
        try:
            cb = self._callbacks[topic]
        except KeyError:
            print("unknown topic {}".format(topic))
        else:
            cb(message)
