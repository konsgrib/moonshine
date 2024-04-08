#!/usr/bin/env python3
import time
import os
from sensors.sensor import Creator
from sensors.sensor_ds import DsCreator
from sensors.sensor_water import WaterSensor
from tools.tool import RelayCreator
import RPi.GPIO as GPIO
import logger
from lcd.lcd import Lcd
from datetime import datetime
from utils import set_environment_variables_from_json
from logger import logger

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, "config.json")


logger.info(f"Reading config {config_path}...")
set_environment_variables_from_json(config_path)


MIN_TEMPERATURE = float(os.environ.get("min-temperature"))
MAX_TEMPERATURE = float(os.environ.get("max-temperature"))
COLD_VALVE_DELAY = int(os.environ.get("cooler-stop-delay"))
# relays
POWER_RELAY_PIN = int(os.environ.get("pins_relay_power_relay_pin"))
POWER_RELAY_2_PIN = int(os.environ.get("pins_relay_power_relay_2_pin"))
COOLER_RELAY_PIN = int(os.environ.get("pins_relay_cooler_relay_pin"))
VALVE_1_PIN = int(os.environ.get("pins_relay_valve_1_relay_pin"))
VALVE_2_PIN = int(os.environ.get("pins_relay_valve_2_relay_pin"))
# display
LCD_DATA_PIN = int(os.environ.get("pins_lcd_data_pin"))
LCD_CLK_PIN = int(os.environ.get("pins_lcd_clk_pin"))
LCD_RESET_PIN = int(os.environ.get("pins_lcd_reset_pin"))

TEMPERATURE_SENSOR_1 = os.environ.get("one-wire_temperature_sensor_1")
TEMPERATURE_SENSOR_2 = os.environ.get("one-wire_temperature_sensor_2")

# water sensors
WATER_PIN_1 = int(os.environ.get("pins_water_level_water_pin_1"))
WATER_PIN_2 = int(os.environ.get("pins_water_level_water_pin_2"))

GPIO_MODE = os.environ.get("gpio-mode")

GPIO.setmode(GPIO.BCM)
GPIO.setup(WATER_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WATER_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Setting up sensors and display
lcd = Lcd(LCD_DATA_PIN, LCD_CLK_PIN, LCD_RESET_PIN)
temperature_1 = DsCreator(TEMPERATURE_SENSOR_1)
temperature_2 = DsCreator(TEMPERATURE_SENSOR_2)
water_1 = WaterSensor(WATER_PIN_1)
cooler_relay = RelayCreator(COOLER_RELAY_PIN)
power_relay = RelayCreator(POWER_RELAY_PIN)
valve_1_relay = RelayCreator(VALVE_1_PIN)
valve_2_relay = RelayCreator(VALVE_2_PIN)


def get_symbol(a):
    ok_list = [1, "On"]
    return "*" if a in ok_list else "-"


def cycle_one() -> None:
    logger.info("Start")
    stop_time = 0
    lcd.clear()
    lcd.display_text("Cycle 1".center(16, "*"), 0, 0)
    lcd.display_text("Starting".center(16, "*"), 0, 1)
    power_state = power_relay.update_state(1)
    cooler_relay.update_state(0)
    logger.info(f"RELAY: {power_state}")

    if power_state.value == 1:
        lcd.display_text("Heating On".center(16, "*"), 0, 2)
    else:
        lcd.display_text("Heating failed".center(16, "*"), 0, 2)
        raise ValueException("Failed to switch power relay on")
    while True:
        try:
            t1 = temperature_1.get_data()
            t2 = temperature_2.get_data()
            w1 = water_1.get_value()
            p1 = power_relay.get_state()
            c1 = cooler_relay.get_state()
            lcd.display_text("P C W".ljust(16, " "), 0, 0)
            lcd.display_text(
                f"{get_symbol(p1)} {get_symbol(c1)} "
                f"{get_symbol(w1.value)}".ljust(16, " "),
                0,
                1,
            )
            print(p1, " ", c1, " ", w1, {c1})
            lcd.display_text(f"Temp1:{t1.value}".ljust(16, " "), 0, 2)
            lcd.display_text(f"Temp2:{t2.value}".ljust(16, " "), 0, 3)
            if t1.value >= MIN_TEMPERATURE and stop_time == 0:
                cooler_relay.update_state(1)
            if t1.value >= MAX_TEMPERATURE and stop_time == 0:
                stop_time = time.time()
                power_relay.update_state(0)
            if stop_time > 0 and stop_time + COLD_VALVE_DELAY * 60 <= time.time():
                cooler_relay.update_state(0)
                lcd.clear()
                lcd.display_text("SUCCEEDED".center(16, "*"), 0, 0)
                break
        except KeyboardInterrupt:
            cooler_relay.update_state(0)
            lcd.clear()
            lcd.display_text("ABORTED".center(16, "*"), 0, 0)
            GPIO.cleanup()
            break
        except Exception as e:
            cooler_relay.update_state(0)
            print(str(e))
            GPIO.cleanup()
            break


if __name__ == "__main__":
    cycle_one()
    # GPIO.cleanup()
