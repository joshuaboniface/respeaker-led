import apa102
import time
import threading
import os
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue

from alexa_led_pattern import AlexaLedPattern
from google_home_led_pattern import GoogleHomeLedPattern

class Pixels:
    PIXELS_N = 12

    def __init__(self, pattern=AlexaLedPattern):
        self.pattern = pattern(show=self.show)

        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

        self.last_direction = None

    def blue(self):
        pixels = [0, 0, 0, 24] * self.PIXELS_N
        self.show(pixels)

    def green(self):
        pixels = [0, 0, 24, 0] * self.PIXELS_N
        self.show(pixels)

    def red(self):
        pixels = [0, 24, 0, 0] * self.PIXELS_N
        self.show(pixels)

    def off(self):
        pixels = [0, 0, 0, 0] * self.PIXELS_N
        self.show(pixels)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def show(self, data):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))
            self.dev.show()


pixels = Pixels()

led_cmd = '/run/led_cmd'

def leds_blue():
    pixels.blue()

def leds_green():
    pixels.green()

def leds_red():
    pixels.red()

def leds_off():
    pixels.off()
    
if __name__ == '__main__':
    if not os.path.exists(led_cmd):
        os.mkfifo(led_cmd)
        os.chown(led_cmd,1000,1000)

    fcmd = open(led_cmd, 'r+', 0)
    while True:
        line = fcmd.readline()
        try:
	    print line.rstrip()
            globals()[line.rstrip()]()
        except:
            pass
