#!/usr/bin/env python3

import sys

from PIL import Image

from inky.auto import auto

from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image

import signal
import RPi.GPIO as GPIO

from inky.inky_uc8159 import CLEAN

BUTTONS = [5, 6, 16, 24]
LABELS = ['A', 'B', 'C', 'D']


# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, C and D respectively
LABELS = ['A', 'B', 'C', 'D']

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

inky = auto(ask_user=True, verbose=True)

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    if pin == 16:
        print ("clearing")
        for _ in range(2):
            for y in range(inky.height - 1):
                for x in range(inky.width - 1):
                    inky.set_pixel(x, y, CLEAN)

            inky.show()
            sleep(5)
    if pin == 24:
        print("photo time")
                
        #Create memory stream
        stream = BytesIO()
        camera = PiCamera()
        camera.resolution = (600, 448)
        sleep(3)
        camera.capture(stream, format='jpeg')
        #'Rewind' stream
        stream.seek(0)
        image = Image.open(stream)
        
        camera.close()

        saturation = 0.7

        '''
        if len(sys.argv) == 1:
            print("""
        Usage: {file} image-file
        """.format(file=sys.argv[0]))
            sys.exit(1)

        image = Image.open(sys.argv[1])
        '''
        #resizedimage = image.resize(inky.resolution)

        if len(sys.argv) > 2:
            saturation = float(sys.argv[2])

        inky.set_image(image, saturation=saturation)
        inky.show()



# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()

