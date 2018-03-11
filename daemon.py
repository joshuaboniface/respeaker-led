
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

    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)

    def speak(self):
        self.put(self.pattern.speak)

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))

        self.dev.show()

pixels = Pixels()

led_cmd = '/run/led_cmd'

def leds_on():
    pixels.wakeup()
    time.sleep(1)

def leds_think():
    pixels.think()
    time.sleep(1)

def leds_off():
    pixels.off()
    time.sleep(1)
    
if __name__ == '__main__':
    if not os.path.exists(led_cmd):
        os.mkfifo(led_cmd, 0666)

    fcmd = open(led_cmd, 'r+', 0)
    while True:
        line = fcmd.readline()
        try:
            globals()[line.rstrip()]()
        except:
            pass
