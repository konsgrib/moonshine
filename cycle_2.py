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

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, "config.json")


logger.info(f"Reading config {config_path}...")
set_environment_variables_from_json(config_path)


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



def get_symbol(a):
    ok_list = [1, "On"]
    return "*" if a in ok_list else "-"


def cycle_two() -> None:
    logger.info("Start")
    process_start_time = time.time()
    t2_temperatures = []
    step_nr = 1
    stop_temperature = 0
    warming_start_time = 0
    warming_end_time = 0
    working_start_time = 0
    working_end_time = 0
    lcd.clear()
    lcd.display_text("Cycle 2".center(16, "*"), 0, 0)
    lcd.display_text("Starting".center(16, "*"), 0, 1)
    power_relay_low.update_state(0)
    cooler_relay.update_state(0)
    power_state = power_relay.update_state(1)
    for _ in range(POWER_IN_CLICKS + 10):
        power_inc_relay.update_state(1)
        time.sleep(0.5)
        power_inc_relay.update_state(0)
        time.sleep(0.5)
    cooler_relay.update_state(0)
    valve_1_relay.update_state(0)
    valve_2_relay.update_state(0)
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
            w2 = water_2.get_value()
            pm = power_relay.get_state()
            pl = 0
            c1 = cooler_relay.get_state()
            v1 = valve_1_relay.get_state()
            v2 = valve_2_relay.get_state()
            lcd.display_text("S Pm W V1 V2 Pr".ljust(16, " "), 0, 0)
            lcd.display_text(
                f"{str(step_nr)} {get_symbol(pm)}  {get_symbol(c1)} "
                f"{get_symbol(v1)}  {get_symbol(v2)}  2".ljust(16, " "),
                0,
                1,
            )
            print(
                pm,
                " ",
                pl,
                " ",
                c1,
                " ",
                v1,
                " ",
                v2,
                " ",
                w1.value,
                " ",
                w2.value,
                " ",
            )
            lcd.display_text(f"Temp1:{t1.value}".ljust(16, " "), 0, 2)
            lcd.display_text(f"Temp2:{t2.value}".ljust(16, " "), 0, 3)
            if t1.value >= MIN_TEMPERATURE and not c1:  # starting cooling process
                step_nr+=1 #2
                print("starting cooling process")
                logger.info("Starting coolant...")
                cooler_relay.update_state(1)
            if t2.value >= POWER_ON_LOW_TEMPERATURE:
                if warming_start_time == 0:  # starting warming process
                    step_nr+=1 #3
                    logger.info("starting warming process")
                    print("starting cooling process")
                    warming_start_time = time.time()
                    logger.info("Starting power low procedure...")
                    print("Starting power low procedure")
                    # decreasing temperature to 70 on controller
                    for _ in range(POWER_IN_CLICKS):
                        power_dec_relay.update_state(1)
                        time.sleep(0.5)
                        power_dec_relay.update_state(0)
                        time.sleep(0.5)
                    step_nr+=1 #4

                    warming_end_time = time.time() + WARMING_TIME * 60
            if step_nr > 3:
                if (
                    0 < warming_end_time <= time.time() and not v1 and not v2
                ):  # droping 1st moonshine
                    step_nr+=1 #5
                    logger.info("droping 1st moonshine")
                    print("droping 1st moonshine")
                    valve_1_relay.update_state(1)
                if not v2 and v1 and w2.value == "On":  # WORK process starting
                    step_nr+=1 #6
                    logger.info("WORK process starting")
                    print("WORK process starting")
                    working_start_time = time.time()
                    working_end_time = working_start_time + WORK_TIME * 60
                    step_nr+=1 #7
                    valve_1_relay.update_state(0)
                    time.sleep(2)
                    valve_2_relay.update_state(1)
                    step_nr+=1 # 8
                    average_temperature = 0.0 #TODO find better solution for this
                if v2:
                    if 0 < working_end_time <= time.time():  # starting to measure t2
                        logger.info("starting to measure t2")
                        print("starting to measure t2")
                        if step_nr < 9:
                            step_nr+=1 #9
                        t2_temperatures.append(t2.value)
                        average_temperature = sum(t2_temperatures) / len(
                            t2_temperatures
                        )
                        logger.info(f"{round(average_temperature, 2)} / {t2.value}")
                        if t2.value > average_temperature + 0.3:  # final pills
                            logger.info("Stopping all processes")
                            print("Stopping all processes")
                            lcd.clear()
                            lcd.display_text("Stopping...".center(16, "*"), 0, 0)
                            power_relay_low.update_state(0)
                            valve_2_relay.update_state(0)
                            cooler_relay.update_state(0)
                            process_end_time = time.time()
                            total_run_time_minutes = round(
                                (process_end_time - process_start_time) / 60, 1
                            )
                            logger.info("Program dinished")
                            lcd.clear()
                            lcd.display_text("Cycle 2 finished".center(16, "*"), 0, 0)
                            lcd.display_text(
                                f"Time: {str(total_run_time_minutes)} min".center(
                                    16, "*"
                                ),
                                0,
                                0,
                            )
                            break

        except KeyboardInterrupt:
            cooler_relay.update_state(0)
            lcd.clear()
            lcd.display_text("ABORTED".center(16, "*"), 0, 0)
            GPIO.cleanup()
            logger.info("manually stopped program")
            break
        except Exception as e:
            cooler_relay.update_state(0)
            print(str(e))
            logger.error(str(e))
            lcd.clear()
            lcd.display_text("ERROR".center(16, "*"), 0, 0)
            GPIO.cleanup()
            break


if __name__ == "__main__":
    cycle_two()
