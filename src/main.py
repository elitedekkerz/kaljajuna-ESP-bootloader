import gc
import os
import utime
import machine
import mqtt_wrap
import sys_config
import network
import micropython


class mqtt_bootloader():
    def __init__(self, mqtt):
        self._mqtt = mqtt
        self._file = None
        self._mqtt.sub("reboot", self._reboot, "sys")
        self._mqtt.sub("file", self._select_file, "sys")
        self._mqtt.sub("write", self._write_file, "sys")
        self._mqtt.sub("read", self._read_file, "sys")
        self._mqtt.sub("run", self.run_app, "sys")
        self._mqtt.sub("led", self._led_set, "sys")

        self._tim = machine.Timer(-1)
        self._tim.init(period=60000, mode=machine.Timer.PERIODIC, callback=self._report_status)

        self._mqtt.pub("connect", "", "sys")
        self._report_status()

        self._led = machine.Pin(2, machine.Pin.OUT)
        print("Bootloader: started")


    def _reboot(self, message):
        print("Bootloader: reboot")
        machine.reset()

    def _select_file(self, message):
        self._file = message

    def _read_file(self, message):
        if self._file:
            with open(self._file, "r") as f:
                self._mqtt.pub("resp", f.read(), "sys")

    def _write_file(self, message):
        if self._file:
            for d in self._file.split("/")[:-1]:
                print(d)
                try:
                    os.mkdir(d)
                except OSError:
                    pass
                os.chdir(d)
                
            os.chdir("/")

            try:
                with open(self._file, "w") as f:
                    f.write(message)
                    self._mqtt.pub("resp", "ok", "sys")
            except Exception as e:
                self._mqtt.pub("error", e, "sys")

    def _report_status(self, id=None):
        mem = "{}/{}".format(gc.mem_alloc(), gc.mem_alloc() + gc.mem_free())
        self._mqtt.pub("status/mem", mem, "sys")
        self._mqtt.pub("status/uptime", utime.time(), "sys")

    def run_app(self, message=""):
        try:
            import app.main
            app.main.run(self._mqtt, message)
        except Exception as e:
            self._mqtt.pub("error", e, "sys")
    
    def _led_set(self, message):
        if message == "on":
            self._led.on()
        if message == "off":
            self._led.off()
            

def main():

    if sys_config.ssid:
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('Connecting to network...')
            sta_if.active(True)
            sta_if.connect(sys_config.ssid, sys_config.password)
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())
        network.WLAN(network.AP_IF).active(False)

    mqtt = mqtt_wrap.mqtt_wrap()
    bootloader = mqtt_bootloader(mqtt)
    gc.collect()

    micropython.mem_info()

    mqtt.check_msg()
    if sys_config.app_autorun:
        bootloader.run_app()

    while True:
        mqtt.check_msg()
        utime.sleep(1)

main()
