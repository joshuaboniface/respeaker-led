# ReSpeaker LED manager

A simple management daemon for the ReSpeaker 4-mic LED ring

## What is it?

The [ReSpeaker 4-mic](https://www.seeedstudio.com/ReSpeaker-4-Mic-Array-for-Raspberry-Pi-p-2941.html) is a Raspberry Pi "hat" which provides an array of 4 microphones and an LED ring, and is used for audio input and user feedback for Pi-based voice control devices such as [my own contraptions](https://www.boniface.me/post/self-hosted-voice-control/). This repository provides a simple daemon to manage the LED components in an asynchronous and extensible way, suitable to be called from another application such as [Kalliope](https://kalliope-project.github.io/) or via the CLI directly.

This daemon is based on the following components:
* The ReSpeaker project's [4mics_hat](https://github.com/respeaker/4mics_hat) examples.
* Martin Erzberger's [APA102_Pi](https://github.com/tinue/APA102_Pi) library (included in the above and retained verbatim here).

## An important note

This is some very alpha quality software right now!

Known issues:
* The client command interface is a security nightmare, and should not in any way be considered safe for public-facing use.
* The Python might be... clunky, in a lot of ways.

In short, it does what I need it to do on a single host and no more. I'll probably continue to improve it as time goes on, however in the meantime please feel free to fork and make it your own!

## How to install it

This repository provides 4 important files: `apa102.py`, `trigger.py`, `daemon.py`, and `respeaker-led.service`.

### `apa102.py`

This file is used as a library by `daemon.py` to interface with the ReSpeaker's APA102 LED array and is hard-forked from Martin Erzberger's library mentioned above.

### `trigger.py`

The client command processor. This tools is incredibly simple, writing the first argument to the `led_cmd` pipe (by default `/run/led_cmd`) of the daemon and then exiting. Usage is described inside the file.

### `daemon.py`

This is the main control daemon. Based on some examples from the ReSpeaker project mentioned above, it runs in a loop scanning for commands (i.e. functions to call) from the `led_cmd` pipe and executing them. All "commands" are simple Python functions which then then call activation functions of the current Pixels() class instance. At the moment this is very clunky and hardcoded (though I do plan to fix that) and all valid commands are listed in the following section.

### `respeaker-led.service`

This is a simple Systemd service unit file which runs `daemon.py` and restarts it on a failure. It features a nifty pre-start command to automatically `git pull` the repo to ensure it's up-to-date (and simplifying administrator or developer work when modifying the daemon - just restart it to get the latest code!) and can be easily enabled from within the repo by running `systemctl enable /path/to/respeaker-led/respeaker-led.service`. Note that for my own purposes, running as a dedicated user on many independent Raspbian instances and pulling from my local protected GitLab instance, this requires a Git deploy SSH key located at `/srv/git-deploy.key`; you should remove this if your setup does not require such security methods (which a clone from GitHub would not).

## Valid functions to call from `trigger.py`

* `leds_off`: Turn all the LEDs off (cancels out all other states except `held` ones).
* `leds_white`: Turn all the LEDs to white (24/24/24 RGB value).
* `leds_blue`: Turn all the LEDs to blue (0/0/24 RGB value).
* `leds_green`: Turn all the LEDs to green (0/24/0 RGB value).
* `leds_red`: Turn all the LEDs to green (24/0/0 RGB value).
* `leds_blink_red`: Set the LEDs to blink red in a 1-second on/off cycle (1/2s on, 1/2 off); this calls the `flash_leds` function that can take a colour as an argument.
* `leds_held_red`: Set the LEDs to stay on red for 3 seconds independent of any `leds_off` command; this calls the `hold_leds` function that can take a colour as an argument.
* `leds_held_green`: Set the LEDs to stay on green for 3 seconds independent of any `leds_off` command; this calls the `hold_leds` function that can take a colour as an argument.

## The use-case

My main use-case for this daemon, and hence my selection of valid colours, "patterns", and functions, is as a visual user feedback device for a [Kalliope](https://kalliope-project.github.io/) instance which does not produce any sound responses. To achieve this, the Kalliope instance calls `trigger.py` directly from the `shell` neuron inside its "hook" orders, which are built-in to Kalliope. The following Kalliope `brain.yml` section provides a description of how the functions and colours are used in this context. In words: on startup `leds_blink_red` for 4.2s to indicate successful startup; immediately on responding to a wake trigger, `leds_white`; on listening start (approximately 0.3-0.5s after wake) `leds_blue` until listening stop `leds_off`; if the triggered order is found, `leds_held_green`, otherwise `leds_held_red`; return to waiting for a trigger with `leds_off` though this does not affect the `held` commands from a response to allow the user to see the result without delaying a new wake cycle.

```
- name: "on-triggered-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_white

- name: "on-waiting-for-trigger-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_off

- name: "on-start-listening-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_blue

- name: "on-stop-listening-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_off

- name: "on-order-found-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_held_green

- name: "on-order-not-found-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_held_red

- name: "on-start-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py leds_blink_red
    - shell:
        cmd: /bin/sleep 4.2 # Just long enough for 4 blinks and a 5th cut off
```

Of course, Kalliope isn't the only possible use-case for this daemon, so feel free to adapt it to suit your needs!

## Licensing

This project is licensed under the GNU GPL version `2.0` or any later version. It includes code from Martin Erzberger licensed under the GNU GPL version `2.0`.
