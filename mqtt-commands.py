import configparser
import os
import time
import subprocess
import paho.mqtt.client as mqtt
import logging

# Set up logging
logging.basicConfig(filename='/var/log/mqtt_commands.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

config_path = "/etc/mqtt-commands.ini"
config = {}
config_last_loaded = 0

def load_config():
    global config, config_last_loaded
    config = {}
    try:
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)
        
        config['mqtt'] = {
            'host': config_parser.get('mqtt', 'host'),
            'port': config_parser.getint('mqtt', 'port'),
            'username': config_parser.get('mqtt', 'username'),
            'password': config_parser.get('mqtt', 'password')
        }
        
        config['topics'] = {
            'command': config_parser.get('topics', 'command'),
            'result': config_parser.get('topics', 'result'),
            'message': config_parser.get('topics', 'message')
        }
        
        config['settings'] = {
            'reload_interval': config_parser.getint('settings', 'reload_interval')
        }
        
        config['commands'] = {
            name: config_parser.get('commands', name)
            for name in config_parser.options('commands')
        }
        
        config_last_loaded = time.time()
        logging.info("Config reloaded")
    except Exception as e:
        logging.error(f"Error loading config: {e}")


# Command to execute shell script
def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT)
        return "OK", output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return "Error", e.output.decode('utf-8')


# MQTT Callback for received messages
def on_message(client, userdata, message):
    payload = message.payload.decode('utf-8')
    logging.info(f"Received command: {payload}")

    command = config['commands'].get(payload)
    if command:
        result, output = execute_command(command)
        client.publish(config['topics']['result'], result)
        client.publish(config['topics']['message'], output)
    else:
        client.publish(config['topics']['result'], "Error")
        client.publish(config['topics']['message'],
                    f"Command {payload} not found")


# Listens to MQTT and checks for reload of config.yaml
def start_mqtt_listener():
    client = mqtt.Client()
    client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])

    client.on_message = on_message

    client.connect(config['mqtt']['host'], config['mqtt']['port'])
    client.subscribe(config['topics']['command'])

    client.loop_start()

    while True:
        if config['settings']['reload_interval'] > 0:
            time_since_last_load = time.time() - config_last_loaded
            if time_since_last_load > config['settings']['reload_interval']:
                load_config()
        time.sleep(60)


if __name__ == "__main__":
    load_config()  # Initial loading of config.yaml
    start_mqtt_listener()
