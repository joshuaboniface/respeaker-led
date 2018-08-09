#!/usr/bin/env python2

# ReSpeaker LED client trigger.py
# Copyright 2018 Joshua Boniface <joshua@boniface.me>
# Released under the GNU GPL version 3.0 or any later version.

def usage():
    print('trigger.py: Send a command to the respeaker-led daemon')
    print('')
    print('Usage:')
    print('')
    print('$ trigger.py <action> [<colour>] [<holdtime>]')
    print('')
    print('Actions:')
    print('  off: Turn off LEDs (unless held)')
    print('  on: Turn on LEDs until next off action')
    print('  flash: Flash LEDs until next off action')
    print('  hold: Keep LEDs on for a specific time unless overridden')
    print('')
    print('Colours:')
    print('  white red blue green yellow cyan magenta')
    print('')
    print('Holdtime:')
    print('  The duration in seconds to keep the LEDs on for hold action')
    print('')
    print('Examples:')
    print('  $ trigger.py off')
    print('  $ trigger.py on red')
    print('  $ trigger.py hold white 5')
    print('  $ trigger.py flash cyan')

# Define our socket to talk to the daemon
cmd_socket = '/run/respeaker-led.sock'

import os, sys

# Get the command from the CLI
try:
    cmd = ' '.join(sys.argv[1:])
# Or set it to an empty string
except:
    cmd = ''

# If cmd is an empty string,
if cmd == '':
    # Print usage and exit with failure
    usage()
    exit(1)

# Try to open the socket writeable
try:
    fcmd = open(cmd_socket, 'w+')
# Or exit with failure
except:
    print("Failed to open socket!")
    exit(1)

# Print argument string to socket
fcmd.write(str(cmd) + '\n')

# Flush and close the socket
fcmd.flush()
fcmd.close()

# Exit with success
exit(0)
