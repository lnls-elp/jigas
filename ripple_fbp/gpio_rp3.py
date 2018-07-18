import RPi.GPIO as gpio
import time


class RaspberryGPIO(object):
    def __init__(self):
        self.rp_pinout = [5, 7, 11, 13, 15, 29, 31, 33]
        self.rp_pinout_relay = {'rl1':5, 'rl2':7, 'rl3': 11, 'rl4':13}


    def initialize(self):
        gpio.setmode(gpio.BOARD)

        for i in self.rp_pinout:
            gpio.setup(i, gpio.OUT)
            time.sleep(0.1)
            gpio.output(i, gpio.LOW)
            time.sleep(0.1)


    def turn_on(self, relay):
        for i in self.rp_pinout:
            gpio.output(i, gpio.LOW)
            time.sleep(0.1)
        gpio.output(self.rp_pinout_relay[relay], gpio.HIGH)


    def turn_off(self, relay):
        gpio.output(self.rp_pinout_relay[relay], gpio.LOW)
