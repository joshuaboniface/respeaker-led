#!/usr/bin/env python2

# ReSpeaker LED client trigger.py
# Copyright 2018 Joshua Boniface <joshua@boniface.me>
# See LICENSE for licensing details

# Usage:
#  $ client.py <daemon.py function>
#
# Valid colours: white, green, blue, red
#
# e.g.
#  $ client.py leds_off
#  $ client.py leds_white
#  $ client.py leds_green
#  $ client.py leds_held_blue [3 seconds]
#  $ client.py leds_blink_red [until leds_off]

import os
import sys

led_cmd = '/run/led_cmd'
cmd = sys.argv[1]

fcmd = open(led_cmd, 'w')
fcmd.write(str(cmd) + '\n')
fcmd.flush()
fcmd.close()
