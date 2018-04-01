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

    def darkblue(self):
        pixels = [0, 0, 0, 24] * self.PIXELS_N
        self.show(pixels)

    def lightblue(self):
        pixels = [0, 12, 12, 24] * self.PIXELS_N
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

def leds_darkblue():
    pixels.darkblue()

def leds_lightblue():
    pixels.lightblue()

def leds_green():
    pixels.green()

def leds_red():
    pixels.red()

def leds_blink_red():
    is_leds_flashing.set()
    t = threading.Thread(name='non-block', target=leds_blinking, args=(is_leds_flashing,'red',))
    print 'test 1'
    t.start()

def leds_off():
    is_leds_flashing.clear()
    pixels.off()

def leds_blinking(is_leds_flashing, colour):
    colours = {
        "blue": pixels.blue,
        "red": pixels.red,
        "green": pixels.green,
    }
    while is_leds_flashing.isSet():
        print colour
        print colours[colour]
        time.sleep(0.3)
        pixels.off()
        time.sleep(0.2)
    is_leds_flashing.clear()
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
