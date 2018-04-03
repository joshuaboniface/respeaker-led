import apa102
import time
import threading
import os
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue

class Pixels:
    PIXELS_N = 12

    def __init__(self):
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def blue(self):
        pixels = [0, 0, 0, 24] * self.PIXELS_N
        self.show(pixels)

    def white(self):
        pixels = [0, 24, 24, 24] * self.PIXELS_N
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
is_leds_flashing = threading.Event()
is_leds_held = threading.Event()

def leds_blue():
    is_leds_held.clear()
    pixels.blue()

def leds_white():
    is_leds_held.clear()
    pixels.white()

def leds_green():
    is_leds_held.clear()
    pixels.green()

def leds_red():
    is_leds_held.clear()
    pixels.red()

def leds_blink_red():
    is_leds_held.clear()
    is_leds_flashing.set()

    t = threading.Thread(name='non-block', target=leds_flashing, args=(is_leds_flashing,'red',))
    t.start()

def leds_held_red():
    holdtime = 3 # default - 3 seconds

    is_leds_flashing.clear()
    is_leds_held.set()

    t = threading.Thread(name='non-block', target=leds_held, args=(is_leds_held,'red',holdtime,))
    t.start()

def leds_off():
    is_leds_flashing.clear()
    if ! is_leds_held.isSet():
        pixels.off()

def leds_flashing(is_leds_flashing, colour):
    colours = {
        "white": pixels.white,
        "blue": pixels.blue,
        "red": pixels.red,
        "green": pixels.green,
    }
    while is_leds_flashing.isSet():
        colours[colour]()
        time.sleep(0.5)
        pixels.off()
        time.sleep(0.5)
    is_leds_flashing.clear()
    return
    
def leds_held(is_leds_held, colour, holdtime):
    colours = {
        "white": pixels.white,
        "blue": pixels.blue,
        "red": pixels.red,
        "green": pixels.green,
    }
    starttime = time.time()
    endtime = starttime + holdtime
    colours[colour]()
    while is_leds_held.isSet() and endtime > time.time():
        time.sleep(0.1)
    pixels.off()
    is_leds_held.clear()
    return
    
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
