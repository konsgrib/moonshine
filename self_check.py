#!/usr/bin/env python3
import time
import os
from sensors.sensor import Creator
from sensors.sensor_ds import DsCreator
from sensors.sensor_water import WaterSensor
from tools.tool import RelayCreator
import RPi.GPIO as GPIO
from lcd.lcd import Lcd
from datetime import datetime
from utils import set_environment_variables_from_json
from logger import logger

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")


set_environment_variables_from_json("config.json")


MIN_TEMPERATURE = float(os.environ.get("min-temperature"))
MAX_TEMPERATURE = float(os.environ.get("max-temperature"))
POWER_ON_LOW_TEMPERATURE = float(os.environ.get("power-on-low-temperature"))

WARMING_TIME = float(os.environ.get("warming-time-minutes"))
WORK_TIME = float(os.environ.get("work-time-minutes"))
WORK_NORMAL_TEMPERATURE = float(os.environ.get("work-normal-temperature"))
WORK_TRESHOLD_TEMPERATURE = float(os.environ.get("work-treshold-temperature"))

COLD_VALVE_DELAY = int(os.environ.get("cooler-stop-delay"))
POWER_IN_CLICKS = int(os.environ.get("power_inc_clicks"))
# relays
POWER_RELAY_PIN = int(os.environ.get("pins_relay_power_relay_pin"))
POWER_RELAY_2_PIN = int(os.environ.get("pins_relay_power_relay_2_pin"))
COOLER_RELAY_PIN = int(os.environ.get("pins_relay_cooler_relay_pin"))
VALVE_1_PIN = int(os.environ.get("pins_relay_valve_1_relay_pin"))
VALVE_2_PIN = int(os.environ.get("pins_relay_valve_2_relay_pin"))
POWER_INC_PIN = int(os.environ.get("pins_relay_power_inc_pin"))
POWER_DEC_PIN = int(os.environ.get("pins_relay_power_dec_pin"))

# display
LCD_DATA_PIN = int(os.environ.get("pins_lcd_data_pin"))
LCD_CLK_PIN = int(os.environ.get("pins_lcd_clk_pin"))
LCD_RESET_PIN = int(os.environ.get("pins_lcd_reset_pin"))

TEMPERATURE_SENSOR_1 = os.environ.get("one-wire_temperature_sensor_1")
TEMPERATURE_SENSOR_2 = os.environ.get("one-wire_temperature_sensor_2")

# water sensors
WATER_PIN_1 = int(os.environ.get("pins_water_level_water_pin_1"))
WATER_PIN_2 = int(os.environ.get("pins_water_level_water_pin_2"))


BTN_1_PIN = int(os.environ.get("pins_buttons_cycle_1_pin"))
BTN_2_PIN = int(os.environ.get("pins_buttons_cycle_2_pin"))
BTN_3_PIN = int(os.environ.get("pins_buttons_cycle_3_pin"))

GPIO_MODE = os.environ.get("gpio-mode")

GPIO.setmode(GPIO.BCM)
GPIO.setup(WATER_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WATER_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Setting up sensors and display
lcd = Lcd(LCD_DATA_PIN, LCD_CLK_PIN, LCD_RESET_PIN)
temperature_1 = DsCreator(TEMPERATURE_SENSOR_1)
temperature_2 = DsCreator(TEMPERATURE_SENSOR_2)
water_1 = WaterSensor(WATER_PIN_1)
water_2 = WaterSensor(WATER_PIN_2)
cooler_relay = RelayCreator(COOLER_RELAY_PIN)
power_relay = RelayCreator(POWER_RELAY_PIN)
power_relay_low = RelayCreator(POWER_RELAY_2_PIN)
valve_1_relay = RelayCreator(VALVE_1_PIN)
valve_2_relay = RelayCreator(VALVE_2_PIN)
power_inc_relay = RelayCreator(POWER_INC_PIN)
power_dec_relay = RelayCreator(POWER_DEC_PIN)


lcd.clear()
lcd.display_text("Self check".center(16, "*"), 0, 0)
lcd.display_text("Starting".center(16, "*"), 0, 1)



relay_pins = [5, 6, 13, 19, 23, 24]
for relay in relay_pins:
    test_relay = RelayCreator(relay)
    lcd.display_text(f"Relay pin: {str(relay)}".center(16, "*"), 0, 1)
    for i in range(10):
        test_relay.update_state(1)
        time.sleep(0.5)
        test_relay.update_state(0)
        time.sleep(0.5)


def callback(channel):
    button_state = GPIO.input(channel)
    if button_state == False:
        if channel == BTN_1_PIN:
            print("Button 1 Pressed")
            lcd.display_text(f"Button 1 Pressed".center(16, "*"), 0, 1)
        elif channel == BTN_2_PIN:
            print("Button 2 Pressed")
            lcd.display_text(f"Button 2 Pressed".center(16, "*"), 0, 1)
        elif channel == BTN_3_PIN:
            print("Button 3 Pressed")
            lcd.display_text(f"Button 3 Pressed".center(16, "*"), 0, 1)
    else:
        if channel == BTN_1_PIN:
            print("Button 1 Released")
            lcd.display_text(f"Button 1 Released".center(16, "*"), 0, 1)
        elif channel == BTN_2_PIN:
            print("Button 2 Released")
            lcd.display_text(f"Button 2 Released".center(16, "*"), 0, 1)
        elif channel == BTN_3_PIN:
            print("Button 3 Released")
            lcd.display_text(f"Button 3 Released".center(16, "*"), 0, 1)



lcd.display_text("".center(16, " "), 0, 3)
lcd.display_text(f"Buttons test".center(16, "*"), 0, 1)

GPIO.add_event_detect(BTN_1_PIN, GPIO.BOTH, callback=callback, bouncetime=200)
GPIO.add_event_detect(BTN_2_PIN, GPIO.BOTH, callback=callback, bouncetime=200)
GPIO.add_event_detect(BTN_3_PIN, GPIO.BOTH, callback=callback, bouncetime=200)

i = 0
while i < 20:
    time.sleep(1)
    i+=1



lcd.display_text("".center(16, " "), 0, 3)
lcd.display_text(f"Termo sensor: {TEMPERATURE_SENSOR_1}".center(16, "*"), 0, 1)
for _ in range(10):
    t1 = temperature_1.get_data()
    lcd.display_text(f"t1: {t1.value}".center(16, " "), 0, 3)
    time.sleep(1)



lcd.display_text("".center(16, " "), 0, 3)
lcd.display_text(f"Termo sensor: {TEMPERATURE_SENSOR_2}".center(16, "*"), 0, 1)
for _ in range(10):
    t2 = temperature_2.get_data()
    lcd.display_text(f"t2: {t2.value}".center(16, " "), 0, 3)
    time.sleep(1)

lcd.display_text("".center(16, " "), 0, 3)

lcd.display_text("".center(16, " "), 0, 3)
lcd.display_text(f"Water sensor: {WATER_PIN_1}".center(16, "*"), 0, 1)
for _ in range(10):
    w1 = water_1.get_value()
    lcd.display_text(f"t1: {w1.value}".center(16, " "), 0, 3)
    time.sleep(1)


lcd.display_text("".center(16, " "), 0, 3)

lcd.display_text("".center(16, " "), 0, 3)
lcd.display_text(f"Water sensor: {WATER_PIN_2}".center(16, "*"), 0, 1)
for _ in range(10):
    w2 = water_2.get_value()
    lcd.display_text(f"t2: {w2.value}".center(16, " "), 0, 3)
    time.sleep(1)

lcd.display_text("".center(16, " "), 0, 3)


lcd.clear()
lcd.display_text("Self check".center(16, "*"), 0, 0)
lcd.display_text("Finished".center(16, "*"), 0, 1)
GPIO.cleanup()


