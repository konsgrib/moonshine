#!/usr/bin/env python3

import os
import RPi.GPIO as GPIO
import time
import logging
from logging.handlers import RotatingFileHandler

import subprocess
import psutil
from utils import set_environment_variables_from_json

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, "watchdog.log")
log_path = "/var/log/watchdog.log"

logger = logging.getLogger('') 
logger.setLevel(logging.INFO) 
handler = RotatingFileHandler(log_path, maxBytes=2000, backupCount=10)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

config_path = os.path.join(dir_path, "config.json")

logging.info(f"Reading config {config_path}...")
set_environment_variables_from_json(config_path)


cycle_1_bt_pin = int(os.environ.get("pins_buttons_cycle_1_pin"))
cycle_2_bt_pin = int(os.environ.get("pins_buttons_cycle_2_pin"))

GPIO.setmode(GPIO.BCM)
GPIO.setup(cycle_1_bt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cycle_2_bt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

logging.info(f"Settings: {cycle_1_bt_pin}...")
logging.info(f"Settings: {cycle_2_bt_pin}...")


def is_process_running(process_name):
    for proc in psutil.process_iter(["name"]):
        if process_name.lower() in proc.info["name"].lower():
            logging.info(f"The process {process_name} already running")
            return True
    logging.info(f"The process {process_name} will be created")
    return False


def callback(channel):
    try:
        if not GPIO.input(channel):
            logging.info("Starting procedure 1!")
            if not is_process_running("cycle_1.py"):
                subprocess.run(
                    [
                        "/home/griban/Projects/moonshine/.venv/bin/python",
                        "/home/griban/Projects/moonshine/cycle_1.py",
                    ]
                )

    except Exception as e:
        logging.error(str(e))


def callback2(channel):
    try:
        if not GPIO.input(channel):
            logging.info("Starting procedure 2!")
            if not is_process_running("cycle_2.py"):
                subprocess.run(
                    [
                        "/home/griban/Projects/moonshine/.venv/bin/python",
                        "/home/griban/Projects/moonshine/cycle_2.py",
                    ]
                )

    except Exception as e:
        logging.error(str(e))



GPIO.add_event_detect(cycle_1_bt_pin, GPIO.BOTH, callback=callback)
GPIO.add_event_detect(cycle_2_bt_pin, GPIO.BOTH, callback=callback2)

while True:
    time.sleep(1)
