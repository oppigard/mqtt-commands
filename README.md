# MQTT Commands

This project listens to MQTT messages and executes corresponding shell commands based on the received payload.  
The intended use case is to be able to run commands on the host, from inside a container.   For example you can create a script in Home Assistant to update its own container.  
The configuration is loaded from an INI file and can be reloaded at a specified interval.

## Requirements

Currently I've only made a build script to create deb packages, which will work on Debian based distro's.  

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/oppigard/mqtt-commands
    cd mqtt-commands
    ```

2. Create virtual environment and install the required Python libraries:
    ```sh
    python -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    ```

3. Build Debian package:
    ```sh
    ./build.sh
    ```

4. Install Debian package:
    ```sh
    sudo apt install ./dist/mqtt-commands-1.0.deb
    ```

## Configuration

The configuration file is located at `/etc/mqtt-commands.ini`. Below is an example configuration:

```ini
[mqtt]
host = localhost
port = 1883
username = user
password = password

[topics]
command = mqtt-commands/command
result = mqtt-commands/result
message = mqtt-commands/message

[settings]
; Reloads config every x Seconds.
; 0 = disabled
reload_interval = 0

[commands]
; command_name = full command without quotes around it
test = echo "test" > /tmp/mqtt_commands_test.txt
```

## Usage
The service can be started/stopped by using:
```sh
sudo service mqtt-commands start
```