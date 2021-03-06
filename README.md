# ReSpeaker LED manager

A simple management daemon for the ReSpeaker 4-mic LED ring

## What is it?

The [ReSpeaker 4-mic](https://www.seeedstudio.com/ReSpeaker-4-Mic-Array-for-Raspberry-Pi-p-2941.html) is a Raspberry Pi "hat" which provides an array of 4 microphones and an LED ring, and is used for audio input and user feedback for Pi-based voice control devices such as [my own contraptions](https://www.boniface.me/post/self-hosted-voice-control/). This repository provides a simple daemon to manage the LED components in an asynchronous and extensible way, suitable to be called from another application such as [Kalliope](https://kalliope-project.github.io/) or via the CLI directly.

This daemon is based on the following components:
* The ReSpeaker project's [4mics_hat](https://github.com/respeaker/4mics_hat) examples.
* Martin Erzberger's [APA102_Pi](https://github.com/tinue/APA102_Pi) library.

## How to use it

### Installation

0. Clone this repo into an available directory (I use `/srv`):
    ```
    cd /srv
    git clone <repo>
    ```
0. Enable the service unit file:
    ```
    systemctl enable /srv/respeaker-led/respeaker-led.service
    ```
0. Start the service:
    ```
    systemctl start respeaker-led.service
    ```
0. Trigger a test command:
    ```
    /srv/respeaker-led/trigger.py hold white 5
    ```

### Python Dependencies

* `gpiozero`

### Main Files

#### `trigger.py`

The client command processor. It sends its arguments to the `cmd_socket` (by default `/run/respeaker-led.sock`) of the daemon and then exits.

#### `daemon.py`

This is the main control daemon. It first opens a command pipe at `cmd_socket`, then runs in a loop scanning for commands from the pipe and executing them.

#### `respeaker-led.service`

A simple Systemd service unit file to run `daemon.py` and restart it on failure. It features a nifty pre-start command to automatically `git pull` the repo to ensure it's up-to-date (and simplifying administrator or developer work when modifying the daemon - just restart it to get the latest code!) Note that for my own purposes, running as a dedicated user on many independent Raspbian instances and pulling from my local protected GitLab instance, this requires a Git deploy SSH key located at `/srv/git-deploy.key`; you should remove this if your setup does not require such security methods (which a clone from GitHub would not). You should also modify the daemon user and group as required.

### Usage of `daemon.py`

`$ daemon.py [<user>:<group>]`

User/Group:

* The user and group names that should own the `cmd_socket` file (mode 644); defaults to `root:root` if not set or invalid

### Usage of `trigger.py`

`$ trigger.py <action> [<colour>] [<holdtime>]`

Actions:
* *none*: Print usage
* off: Turn off LEDs (unless held)
* on: Turn on LEDs until next off action
* flash: Flash LEDs until next off action
* hold: Keep LEDs on for some time unless overridden

Colours:

* white
* red
* blue
* green
* yellow
* cyan
* magenta

Holdtime:

* The duration in seconds to keep the LEDs on (`hold` action only); defaults to 3 seconds if not set

## The use-case

For a full description of the entire project, please see [this post on my website](https://www.boniface.me/post/self-hosted-voice-control/).

My main use-case for this daemon, and hence my selection of valid colours, "patterns", and functions, is as a visual user feedback device for a [Kalliope](https://kalliope-project.github.io/) instance which does not produce any sound responses. To achieve this, the Kalliope instance calls `trigger.py` directly from the `shell` neuron inside its "hook" orders, which are built-in to Kalliope. The following Kalliope `brain.yml` section provides a description of how the functions and colours are used in this context.

```
- name: "on-triggered-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py on white

- name: "on-waiting-for-trigger-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py off

- name: "on-start-listening-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py on blue

- name: "on-stop-listening-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py off

- name: "on-order-found-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py hold green 3

- name: "on-order-not-found-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py hold red 3

- name: "on-start-synapse"
  signals: []
  neurons:
    - shell:
        cmd: /srv/respeaker-led/trigger.py flash magenta
    - shell:
        cmd: /bin/sleep 4.5 # Just long enough for 5 blinks
```

Of course, Kalliope isn't the only possible use-case for this daemon, so feel free to adapt it to suit your needs!

## Licensing

This project is licensed under the GNU GPL version `3.0` or any later version.
