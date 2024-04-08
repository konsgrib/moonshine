import RPi.GPIO as GPIO
import time

from .sensor import Creator, Sensor, SensorValue


# class WaterSensorCreator(Creator):
#     def __init__(self, pin) -> None:
#         self.pin = pin

#     GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#     def factory_method(self, )


class WaterSensor(Sensor):
    def __init__(
        self,
        bcm_pin_number,
    ) -> None:
        self.bcm_pin_number = bcm_pin_number
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.bcm_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_value(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bcm_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        current_value = GPIO.input(self.bcm_pin_number)
        if current_value == 0:
            result = "On"
        elif current_value == 1:
            result = "Off"
        else:
            result = "Unknown"
        return SensorValue(200, result, "OK")
