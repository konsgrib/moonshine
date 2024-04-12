#!/usr/bin/env python3

import os
import RPi.GPIO as GPIO
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

import subprocess
import psutil
from utils import set_environment_variables_from_json, get_one_wire_device_ids
from lcd.lcd import Lcd

dir_path = os.path.dirname(os.path.realpath(__file__))

log_path = "/var/log/watchdog.log"
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

logger = logging.getLogger("")
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

LCD_DATA_PIN = int(os.environ.get("pins_lcd_data_pin"))
LCD_CLK_PIN = int(os.environ.get("pins_lcd_clk_pin"))
LCD_RESET_PIN = int(os.environ.get("pins_lcd_reset_pin"))

logging.info(f"Settings: {cycle_1_bt_pin}...")
logging.info(f"Settings: {cycle_2_bt_pin}...")


lcd = Lcd(LCD_DATA_PIN, LCD_CLK_PIN, LCD_RESET_PIN)
lcd.clear()
lcd.display_text("                ".center(16, " "), 0, 0)
lcd.display_text("                ".center(16, " "), 0, 1)
lcd.display_text("Press any key".center(16, " "), 0, 2)


def is_process_running(process_path):
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        if process_path.lower() in ' '.join(proc.info['cmdline']).lower():
            logging.info(f"The process {process_path} already running")
            return True
    return False


def callback(channel):
    try:
        if not GPIO.input(channel):
            logging.info("Starting procedure 1!")
            if not is_process_running("cycle_1.py"):
                subprocess.run(
                    [
                        "/home/pi/Projects/moonshine/.venv/bin/python",
                        "/home/pi/Projects/moonshine/cycle_1.py",
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
                        "/home/pi/Projects/moonshine/.venv/bin/python",
                        "/home/pi/Projects/moonshine/cycle_2.py",
                    ]
                )

    except Exception as e:
        logging.error(str(e))




def callback(channel):
    button_state = GPIO.input(channel)
    if button_state == False:
        if channel == cycle_1_bt_pin:
            print("Button 1 Pressed")
            logging.info("Starting procedure 1!")
            if not is_process_running("cycle_1.py"):
                  subprocess.run(
                    [
                        "/home/pi/Projects/moonshine/.venv/bin/python",
                        "/home/pi/Projects/moonshine/cycle_1.py",
                    ]
                )              
        elif channel == cycle_2_bt_pin:
            print("Button 2 Pressed")
            logging.info("Starting procedure 2!")
            if not is_process_running("cycle_2.py"):
                subprocess.run(
                    [
                        "/home/pi/Projects/moonshine/.venv/bin/python",
                        "/home/pi/Projects/moonshine/cycle_2.py",
                    ]
                )






file_path = os.path.join(dir_path, "w1.txt")
get_one_wire_device_ids(file_path)

GPIO.add_event_detect(cycle_1_bt_pin, GPIO.BOTH, callback=callback)
GPIO.add_event_detect(cycle_2_bt_pin, GPIO.BOTH, callback=callback2)

while True:
    time.sleep(1)
    now = datetime.now()
    is_cycle_1_running = is_process_running("cycle_1.py")
    is_cycle_2_running = is_process_running("cycle_2.py")

    if not (is_cycle_1_running or is_cycle_2_running):
        d_now_str = now.strftime("%Y-%m-%d")
        t_now_str = now.strftime("%H:%M:%S")
        lcd.display_text(f"{d_now_str}".center(16, " "), 0, 0)
        lcd.display_text(f"{t_now_str}".center(16, " "), 0, 1)
