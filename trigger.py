#!/usr/bin/env python3

import os
import sys

led_cmd = '/run/led_cmd'
cmd = sys.argv[1]

fcmd = open(led_cmd, 'w')
fcmd.write(str(cmd) + '\n')
fcmd.flush()
fcmd.close()
