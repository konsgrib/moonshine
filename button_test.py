import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

button_pin1 = 9  # Change as per your 1st button connection
button_pin2 = 10  # Change as per your 2nd button connection
button_pin3 = 11  # Change as per your 2nd button connection


GPIO.setup(button_pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def callback(channel):
    button_state = GPIO.input(channel)
    if button_state == False:
        if channel == button_pin1:
            print("Button 1 Pressed")
        elif channel == button_pin2:
            print("Button 2 Pressed")
        elif channel == button_pin3:
            print("Button 3 Pressed")
    else:
        if channel == button_pin1:
            print("Button 1 Released")
        elif channel == button_pin2:
            print("Button 2 Released")
        elif channel == button_pin3:
            print("Button 3 Released")

try:
    GPIO.add_event_detect(button_pin1, GPIO.BOTH, callback=callback, bouncetime=200)
    GPIO.add_event_detect(button_pin2, GPIO.BOTH, callback=callback, bouncetime=200)
    GPIO.add_event_detect(button_pin3, GPIO.BOTH, callback=callback, bouncetime=200)
    while True:
        time.sleep(0.01)
except KeyboardInterrupt: 
    GPIO.cleanup()  # cleanup all GPIO
