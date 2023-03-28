#!/usr/bin/env python3

import os
import sys
from inky.auto import auto
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
from PIL import UnidentifiedImageError
import signal
import RPi.GPIO as GPIO
from inky.inky_uc8159 import CLEAN

image_files = []
current_index = -1

def clear_display():
    for _ in range(2):
        for y in range(inky.height - 1):
            for x in range(inky.width - 1):
                inky.set_pixel(x, y, CLEAN)

        inky.show()
        sleep(5)

def display_image(path):
    try:
        image = Image.open(path)
    except UnidentifiedImageError:
        print("Can't open image")
        clear_display()
        return
    #Display image
    saturation = 0.7
    inky.set_image(image, saturation=saturation)
    inky.show()

def get_image_files():
    global image_files, current_index
    if not os.path.exists("images"):
        os.makedirs("images")
    image_files = [os.path.join("images", f) for f in os.listdir("images") if f.endswith(".jpg")]
    image_files.sort()
    if len(image_files) > 0:
        current_index = len(image_files) - 1
        display_image(image_files[current_index])

def show_prev_image():
    global current_index
    if current_index > 0:
        current_index -= 1
        display_image(image_files[current_index])

def show_next_image():
    global current_index
    if current_index < len(image_files) - 1:
        current_index += 1
        display_image(image_files[current_index])

def delete_current_image():
    global image_files, current_index
    if len(image_files) == 0:
        print("No images to delete.")
        return
    os.remove(image_files[current_index])
    del image_files[current_index]
    if current_index == len(image_files):
        current_index -= 1
    if len(image_files) > 0:
        display_image(image_files[current_index])
    else:
        clear_display()

def save_image(image):
    global image_files, current_index
    current_index = len(image_files)
    image_path = "image" + str(current_index) + ".jpg"
    image_files.append(image_path)
    image.save(image_path, 'JPEG')
    print(f"Saved image to {image_path}")
    display_image(image_path)

def take_photo():
    #Capture image 
    stream = BytesIO()
    camera = PiCamera()
    camera.resolution = (600, 448)
    sleep(3)
    camera.capture(stream, format='jpeg')
    #'Rewind' stream
    stream.seek(0)
    image = Image.open(stream)
    camera.close()
    #Save image
    save_image(image)

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin, image_files, ):
    if pin == 16:
        print ("delete current image")

    if pin == 24:
        print("photo time")
        take_photo()
    if pin == 6:
        print("next photo")
        show_next_image()
    if pin == 5:
        print("previous photo")
        show_prev_image()

def main():
    #Button config
    BUTTONS = [5, 6, 16, 24] # Gpio pins for each button (from top to bottom)
    LABELS = ['A', 'B', 'C', 'D'] # These correspond to buttons A, B, C and D respectively
    GPIO.setmode(GPIO.BCM) # Set up RPi.GPIO with the "BCM" numbering scheme
    # Buttons connect to ground when pressed, so we should set them up
    # with a "PULL UP", which weakly pulls the input signal to 3.3V.
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #Inky settings
    inky = auto(ask_user=True, verbose=True)
    saturation = 0.7

    #Get current filesystem, last current_index
    get_image_files()
    current_index = 0

    #Add button event detect
    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)
    signal.pause()

if __name__ == "__main__":
    main()