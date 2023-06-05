#!/usr/bin/env python3

# ResSpeaker LED feedback trigger client
#
# Provides a convenient command to trigger actions to the ReSpeaker LED
# feedback daemon ("respeaker-led.py").
#
# Run without arguments for help.
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
import sys

def usage():
    print('trigger.py: Send a command to the respeaker-led daemon')
    print('')
    print('Usage:')
    print('')
    print('$ trigger.py <action> <colour> [<extarg>]')
    print('')
    print('Actions:')
    print('  off: Turn off LEDs; {colour} is ignored/optional')
    print('  on: Turn on LEDs until next action')
    print('  flash: Flash LEDs until next action; {extarg} is the optional flash interval (default 1s)')
    print('  spin: Spin the LEDs until next action; {extarg} is the optional cycle time (default 1s)')
    print('  hold: Keep LEDs on for {extarg} seconds (default 5s) unless overridden')
    print('')
    print('Colours:')
    print('  white red blue green yellow cyan magenta')
    print('')
    print('Examples:')
    print('  $ trigger.py off')
    print('  $ trigger.py on red')
    print('  $ trigger.py flash cyan')
    print('  $ trigger.py spin yellow')
    print('  $ trigger.py hold white')

# Define our socket to talk to the daemon
COMMAND_SOCKET = '/run/shm/respeaker-led.sock'

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
    fcmd = open(COMMAND_SOCKET, 'wb+', buffering=0)
# Or exit with failure
except Exception as e:
    print(f"Failed to open socket! Error: {e}")
    exit(1)

# Print argument string to socket
fcmd.write(f"{cmd}".encode())

# Flush and close the socket
fcmd.flush()
fcmd.close()

# Exit with success
exit(0)
