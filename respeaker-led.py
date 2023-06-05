#!/usr/bin/env python

# ReSpeaker LED feedback daemon
#
# Provides visual feedback via the LEDs on the ReSpeaker. Can execute various
# patterns with various (basic) colours via a few standard commands or a more
# flexible colour interface.
#
# Communicated to via a socket listening as a {user}:{group} pair specified on
# the command line at startup. The included "trigger.py" can act as a client.
#
#    Copyright (C) 2017-2023 Joshua M. Boniface <joshua@boniface.me>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################


import os
import signal
from sys import argv
from threading import Thread, Event
from multiprocessing import Process
from time import sleep
from pwd import getpwnam
from gpiozero import LED
from apa102_pi.driver.apa102 import APA102
from pathlib import Path


COMMAND_SOCKET = "/run/shm/respeaker-led.sock"


class Pixels:
    """
    Defines the pixels on the board as well as the main low-level driver functions
    """

    # We are written for the 4-mic hat, which has 12 pixels (LEDs)
    PIXELS_N = 12

    # We set a global brightness for the LEDs here; 31 is maximum
    GLOBAL_BRIGHTNESS = 31

    def __init__(self):
        """
        Initialize the APA102, set power on, and prepare threads
        """
        self.dev = APA102(num_led=self.PIXELS_N, global_brightness=self.GLOBAL_BRIGHTNESS)
        self.power = LED(5)
        self.power.on()

        self.proc = None

    def start(self, target, *args):
        self.proc = Process(target=target, args=args)
        self.proc.start()

    def stop(self):
        try:
            self.proc.terminate()
        except Exception:
            # If we can't terminate, we just move to switching pixels off
            pass
        self.off()

    def show(self, pixel, colour):
        """
        Activate a specific pixel with a specific colour

        {colour} is a tuple of ({red}, {green}, {blue})
        """
        self.dev.set_pixel(pixel, colour[0], colour[1], colour[2])
        self.dev.show()

    def off(self):
        """
        Turn off all pixels
        """
        for i in range(self.PIXELS_N):
            self.show(i, (0, 0, 0))

    def solid(self, colour):
        """
        Show a solid colour ({red}, {green}, {blue}) on all pixels until stopped
        """
        for i in range(self.PIXELS_N):
            self.show(i, colour)

    def hold(self, colour, holdtime=5):
        """
        Hold a solid colour for {holdtime} or until stopped
        """
        self.solid(colour)
        sleep(holdtime)
        self.off()

    def flash(self, colour, interval=1):
        """
        Flash a solid colour at {interval} (half on, half off) until stopped
        """
        while True:
            self.solid(colour)
            sleep(interval/2)
            self.off()
            sleep(interval/2)

    def spin(self, colour, interval=1):
        """
        Spin a colour around the pixels, with each rotation taking {interval}, until stopped
        """
        while True:
            for i in range(self.PIXELS_N):
                self.show(i, colour)
                sleep(interval/self.PIXELS_N)
                self.show(i, (0, 0, 0))

class Daemon:
    def parse_command_name(self, name):
        command_map = {
            None:     self.pixels.stop,
            'off':    self.pixels.stop,
            'stop':   self.pixels.stop,
            'on':     self.pixels.solid,
            'solid':  self.pixels.solid,
            'hold':   self.pixels.hold,
            'flash':  self.pixels.flash,
            'blink':  self.pixels.flash,
            'spin':   self.pixels.spin,
            'rotate': self.pixels.spin,
        }
    
        try:
            return command_map[name]
        except KeyError:
            print(f"Invalid command '{name}', selecting 'off' instead")
            return None
    
    def parse_colour_name(self, name):
        colour_map = {
            None:       (0,   0,   0),
            'red':      (255, 0,   0),
            'green':    (0,   255, 0),
            'blue':     (0,   0,   255),
            'yellow':   (255, 255, 0),
            'cyan':     (0,   255, 255),
            'magenta':  (255, 0,   255),
            'white':    (255, 255, 255),
        }
    
        try:
            return colour_map[name]
        except KeyError:
            print(f"Invalid colour '{name}', selecting 'white' instead")
            return colour_map['white']
    
                
    def __init__(self):
        # Setup the socket listener
        try:
            user, group = argv[1].split(':')
            uid = getpwnam(user).pw_uid
            gid = getpwnam(user).pw_gid
        except Exception:
            uid = os.getuid()
            gid = os.getgid()
    
        if os.path.exists(COMMAND_SOCKET):
            print('Clearing stale socket')
            os.remove(COMMAND_SOCKET)
    
        print(f'Creating new listener socket {COMMAND_SOCKET}')
        self.fifo = Path(COMMAND_SOCKET)
        os.mkfifo(COMMAND_SOCKET)
        os.chown(COMMAND_SOCKET, uid, gid)

        # Create the pixel instance
        self.pixels = Pixels()
        self.pixels.off()
    
    def stop(self):
        print()
        print("Terminating")
        self.pixels.stop()
        os.remove(COMMAND_SOCKET)

    def run(self):
        # Main listener loop
        while True:
            print('Listening...')
            data = self.fifo.read_text().split()
            if not data:
                sleep(0.1)
                continue
    
            # Commands come in with the form:
            #   {action} {colour_name} {extra_args}
            command = data[0]
    
            try:
                colour = data[1]
            except IndexError:
                colour = None
    
            try:
                extarg = int(data[2])
            except IndexError:
                extarg = None
    
            print(f"Received command: {command}; colour: {colour}; extra arg: {extarg}")
    
    
            # Stop any current actions (this is all that's needed for off and stop)
            self.pixels.stop()
    
            # Execute the new command
            if command not in ['off', 'stop']:
                action = self.parse_command_name(command)
                if action is None:
                    continue
    
                colours = self.parse_colour_name(colour)
    
                if extarg is not None:
                    self.pixels.start(action, colours, extarg)
                else:
                    self.pixels.start(action, colours)
   
if __name__ == '__main__':
    daemon = Daemon()
    try:
        daemon.run()
    except:
        pass
    finally:
        daemon.stop()
