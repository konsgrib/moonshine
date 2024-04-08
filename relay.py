import RPi.GPIO as GPIO
import sys
import traceback

# pin =5, 6


def set_relay_state(pin, state):
    try:
        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, state)
        return state
    except KeyboardInterrupt:
        print("Extit pressed Ctrl+C")
    except Exception as e:
        print(f"Another exception: {str(e)}")
        traceback.print_exc(limit=2, file=sys.stdout)
