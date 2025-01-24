import adafruit_rgbled
import board
import digitalio
import rotaryio
import storage
import time
import usb_hid

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from button_handler import ButtonHandler, ButtonInput, ButtonInitConfig
from keypad import Keys

print("== Pi Pico multifunction knob 3.0 ==")

# Debug
debug = False

# Pins
CLK_PIN = board.GP2
DT_PIN = board.GP3
SW_PIN = board.GP4
RED_LED = board.GP20
GREEN_LED = board.GP19
BLUE_LED = board.GP18

totalMode = 3
currentMode = 0

cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

encoder = rotaryio.IncrementalEncoder(CLK_PIN, DT_PIN)
last_position = encoder.position

led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)


def millis():
    return time.monotonic() * 1000


def log(message):
    if debug:
        print(message)


def blinkWhenPluggingIn():
    led.color = 0xFFFFFF


def ledMode2():
    led.color = 0x008833


def ledMode1():
    led.color = 0x880033


def ledMode0():
    led.color = 0x0000DD


def ccw():
    log("Knob: turned left, mode = " + str(currentMode))
    if currentMode == 0:
        # Volume decrement
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
    if currentMode == 1:
        # Mouse wheel increment
        mouse.move(wheel=2)
    if currentMode == 2:
        # Brightness decrement
        cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)


def cw():
    log("Knob: turned right, mode = " + str(currentMode))
    if currentMode == 0:
        # Volume increment
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
    if currentMode == 1:
        # Mouse wheel decrement
        mouse.move(wheel=-2)
    if currentMode == 2:
        # Brightness increment
        cc.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)


def double_press():
    global currentMode
    if currentMode == 0:
        cc.send(ConsumerControlCode.MUTE)
    if currentMode == 1:
        keyboard.press(Keycode.COMMAND, Keycode.L)
        keyboard.release_all()
        long_press()
        return
    if currentMode == 2:
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        time.sleep(1)
        keyboard.press(Keycode.NINE, Keycode.TWO, Keycode.EIGHT, Keycode.SEVEN)
        keyboard.release_all()
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        long_press()


def short_press():
    global currentMode
    log("Knob: short press detected, mode = " + str(currentMode))
    if currentMode == 0:
        log("PLAY_PAUSE")
        cc.send(ConsumerControlCode.PLAY_PAUSE)
    elif currentMode == 1:
        mouse.click(Mouse.LEFT_BUTTON)
    elif currentMode == 2:
        log("TODO short press in mode 2")


def long_press():
    global totalMode
    global currentMode
    currentMode += 1
    currentMode %= totalMode
    log("Knob Mode: " + str(currentMode))


def hold():
    global currentMode
    log("Knob: hold detected, mode = " + str(currentMode))


def reset_keyboard(force=False):
    global keyboard, cc

    if force:
        time.sleep(1)
        log("Resetting keyboard..")
        cc = ConsumerControl(usb_hid.devices)
        keyboard = Keyboard(usb_hid.devices)
    else:
        if cc is None:
            time.sleep(1)
            log("ConsumerControl not initialized. Trying again..")
            cc = ConsumerControl(usb_hid.devices)
        if keyboard is None:
            time.sleep(1)
            log("Keyboard not initialized. Trying again..")
            keyboard = Keyboard(usb_hid.devices)


actions = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, callback=double_press),
    ButtonInput(ButtonInput.SHORT_PRESS, callback=short_press),
    ButtonInput(ButtonInput.LONG_PRESS, callback=long_press),
    ButtonInput(ButtonInput.HOLD, callback=hold),
}

scanner = Keys([SW_PIN], value_when_pressed=False)
button_config = ButtonInitConfig(True, 350, 900, 2)
button_handler = ButtonHandler(scanner.events, actions, 1, {0: button_config})


def loop():
    global currentMode
    global last_position

    if currentMode == 0:
        ledMode0()
    if currentMode == 1:
        ledMode1()
    if currentMode == 2:
        ledMode2()
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            cw()
        log(current_position)
    elif position_change < 0:
        for _ in range(-position_change):
            ccw()
        log(current_position)
    last_position = current_position

    # Press
    try:
        button_handler.update()
        time.sleep(0.0025)
    except Exception as e:
        log("An error occurred: {}".format(e))
        reset_keyboard(True)


if __name__ == "__main__":
    while True:
        # try except just in case there are any errors that might occur for any reason. Make sure it keeps running.
        try:
            loop()
        except Exception as e2:
            log("An error in the loop occurred: {}".format(e2))
            reset_keyboard(True)