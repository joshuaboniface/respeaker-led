#!/usr/bin/env python3

# ReSpeaker LED daemon.py
# Copyright 2018 Joshua Boniface <joshua@boniface.me>
# See LICENSE for licensing details

cmd_socket = '/run/respeaker-led.sock'

import os, sys, threading, time, queue
from driver import apa102
from gpiozero import LED
from pwd import getpwnam

#
# Pixel class definition
#
class Pixels:
    PIXELS_N = 12

    def __init__(self):
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

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

    def on(self, red, green, blue):
        pixels = [0, red, green, blue] * self.PIXELS_N
        self.show(pixels)

    def off(self):
        pixels = [0, 0, 0, 0] * self.PIXELS_N
        self.show(pixels)

# Define an instance of the class
pixels = Pixels()

#
# Threading events
#
is_leds_flashing = threading.Event()
is_leds_holding = threading.Event()

#
# Main functions
#
def leds_off():
    # Clear all flashing events and wait for thread to stop
    is_leds_flashing.clear()
    time.sleep(0.1)

    # If we're not held,
    if not is_leds_holding.isSet():
        # Turn off LEDs
        pixels.off()

def leds_on(red, blue, green):
    # Clear all flashing and holding events and wait for threads to stop
    is_leds_flashing.clear()
    is_leds_holding.clear()
    time.sleep(0.1)

    # Turn on LEDs
    pixels.on(red, blue, green)

def leds_flash(red, blue, green):
    # Clear all flashing and holding events and wait for threads to stop
    is_leds_flashing.clear()
    is_leds_holding.clear()
    time.sleep(0.1)

    # Set the event
    is_leds_flashing.set()

    # Define and start the threaded task
    t = threading.Thread(name='non-block', target=flash, args=(is_leds_flashing, red, blue, green, ))
    t.start()

def leds_hold(red, blue, green, holdtime):
    # Clear all flashing and holding events and wait for threads to stop
    is_leds_flashing.clear()
    is_leds_holding.clear()
    time.sleep(0.1)

    # Set the event
    is_leds_holding.set()

    # Define and start the threaded task
    t = threading.Thread(name='non-block', target=hold, args=(is_leds_holding, red, blue, green, holdtime, ))
    t.start()

#
# Threaded functions
#
def flash(event, red, blue, green):
    # Set default interval
    interval = 0.5

    # As long as the event is set,
    while event.isSet():
        # Turn on LEDs and sleep for interval
        pixels.on(red, blue, green)
        time.sleep(interval)
        # Turn off LEDs and sleep for interval
        pixels.off()
        time.sleep(interval)

    # Clear the event
    event.clear()

def hold(event, red, blue, green, holdtime):
    # Determine the start and end times of the hold
    starttime = time.time()
    endtime = starttime + holdtime

    # Turn on LEDs
    pixels.on(red, blue, green)

    # As long as the event is set and we haven't passed endtime,
    while event.isSet() and endtime > time.time():
        # Wait a tiny bit
        time.sleep(0.1)

    # Turn off LEDs
    pixels.off()

    # Clear the event
    event.clear()

#
# Helper functions
#
def get_value(line, index, default, errtxt):
    # Try to get the value at line[index]
    try:
        value = line[index]
    # If it doesn't exist,
    except IndexError:
        # And a default is set,
        if default != None:
            # Set the default
            value = default
        else:
            # Or return errtxt
            print('%s' % errtxt)
            return None

    # Return the value
    return value

def get_rgb(colour):
    # Pixel colour definitions
    colours = {
        "red": "24,0,0",
        "green": "0,24,0",
        "blue": "0,0,24",
        "yellow": "24,24,0",
        "cyan": "0,24,24",
        "magenta": "24,0,24",
        "white": "24,24,24",
    }

    # Return the per-colour pixel values
    return colours[colour].split(',')

#
# Main loop
#
if __name__ == '__main__':
    # Try to get our user and group for the socket from the first argument
    try:
        user, group = sys.argv[1].split(':')
    # Or just set the default of root:root
    except:
        user = 'root'
        group = 'root'

    # Convert user and group names to uid and gid for the socket
    uid = getpwnam(user).pw_uid
    gid = getpwnam(user).pw_gid

    # If the socket already exists,
    if os.path.exists(cmd_socket):
        # Remove it
        print('Removing stale socket at %s' % cmd_socket)
        os.remove(cmd_socket)

    # Create a new socket and change ownership to user:group
    print('Creating new socket at %s owned by %s:%s' % (cmd_socket, user, group))
    os.mkfifo(cmd_socket)
    os.chown(cmd_socket,uid,gid)

    # Open socket
    print('Opening socket at %s' % cmd_socket)
    fcmd = open(cmd_socket, 'r')

    # Listen for events on socket
    print('Listening...')
    while True:
        # Get a line from the socket
        try:
            line = fcmd.readlines()[0].rstrip().split()
        except:
            continue
        print('%s' % str(line))

        # Determine the command
        command = get_value(line, 0, None, 'No command specified!')

        # > off
        if command == 'off':
            # Turn off LEDs
            leds_off()

        # > on <colour>
        elif command == 'on':
            # Determine the colour
            colour = get_value(line, 1, None, 'No colour specified!')

            # If colour is unset,
            if colour == None:
                # Abort the command
                continue

            # Turn on LEDs as colour
            red, green, blue = get_rgb(colour)
            leds_on(red, green, blue)

        # > flash <colour>
        elif command == 'flash':
            # Determine the colour
            colour = get_value(line, 1, None, 'No colour specified!')

            # If colour is unset,
            if colour == None:
                # Abort the command
                continue

            # Flash LEDs as colour
            red, green, blue = get_rgb(colour)
            leds_flash(red, green, blue)

        # > held <colour> <time>
        elif command == 'hold':
            # Determine the colour and time to hold (seconds, default of 3)
            colour = get_value(line, 1, None, 'No colour specified!')
            holdtime = int(get_value(line, 2, 3, None))

            # if colour or time is unset,
            if colour == None or holdtime == None:
                # Abort the command
                continue

            # Hold LEDs as colour for time
            red, green, blue = get_rgb(colour)
            leds_hold(red, green, blue, holdtime)

        # Otherwise,
        else:
            # This was an invalid command
            print('Invalid command!')
