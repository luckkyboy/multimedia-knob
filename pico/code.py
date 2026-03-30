import rotaryio
import time
import usb_hid

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from button_handler import ButtonHandler, ButtonInput, ButtonInitConfig
from keypad import Keys

try:
    from .actions import KnobActions
    from .config import (
        BLUE_LED,
        BUTTON_ENABLE_DOUBLE_PRESS,
        BUTTON_HOLD_INTERVAL,
        BUTTON_LONG_PRESS_MS,
        BUTTON_SHORT_PRESS_MS,
        CLK_PIN,
        DEBUG,
        DT_PIN,
        LED_ERROR,
        GREEN_LED,
        LOOP_DELAY_SECONDS,
        RED_LED,
        SW_PIN,
    )
    from .modes import build_modes
    from .runtime import KnobRuntime
except ImportError:
    from actions import KnobActions
    from config import (
        BLUE_LED,
        BUTTON_ENABLE_DOUBLE_PRESS,
        BUTTON_HOLD_INTERVAL,
        BUTTON_LONG_PRESS_MS,
        BUTTON_SHORT_PRESS_MS,
        CLK_PIN,
        DEBUG,
        DT_PIN,
        LED_ERROR,
        GREEN_LED,
        LOOP_DELAY_SECONDS,
        RED_LED,
        SW_PIN,
    )
    from modes import build_modes
    from runtime import KnobRuntime

print("== Pi Pico multifunction knob 3.0 ==")

cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
device_actions = KnobActions(cc, mouse, keyboard)
modes = build_modes(device_actions)

encoder = rotaryio.IncrementalEncoder(CLK_PIN, DT_PIN)
last_position = encoder.position

import adafruit_rgbled

led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)


def log_debug(message):
    if DEBUG:
        print(message)


def log_error(message):
    print(message)


runtime = KnobRuntime(
    modes,
    led,
    log_debug=log_debug,
    log_error=log_error,
    recover_hid=lambda force=False: reset_hid_devices(force=force),
    unhealthy_color=LED_ERROR,
)


def double_press():
    mode_before = runtime.current_mode
    runtime.handle_double_press()
    if mode_before in (1, 2):
        long_press()


def short_press():
    runtime.handle_short_press()


def long_press():
    runtime.advance_mode()


def hold():
    runtime.handle_hold()


def reset_keyboard(force=False):
    reset_hid_devices(force=force)


def reset_hid_devices(force=False):
    global cc, keyboard, mouse, device_actions, modes, runtime

    if force:
        time.sleep(1)
        log_debug("Resetting HID devices..")
        cc = ConsumerControl(usb_hid.devices)
        keyboard = Keyboard(usb_hid.devices)
        mouse = Mouse(usb_hid.devices)
    else:
        if cc is None:
            time.sleep(1)
            log_debug("ConsumerControl not initialized. Trying again..")
            cc = ConsumerControl(usb_hid.devices)
        if keyboard is None:
            time.sleep(1)
            log_debug("Keyboard not initialized. Trying again..")
            keyboard = Keyboard(usb_hid.devices)
        if mouse is None:
            time.sleep(1)
            log_debug("Mouse not initialized. Trying again..")
            mouse = Mouse(usb_hid.devices)

    device_actions = KnobActions(cc, mouse, keyboard)
    modes = build_modes(device_actions)
    runtime.modes = modes
    runtime.unhealthy = False
    runtime.apply_mode_led()


actions = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, callback=double_press),
    ButtonInput(ButtonInput.SHORT_PRESS, callback=short_press),
    ButtonInput(ButtonInput.LONG_PRESS, callback=long_press),
    ButtonInput(ButtonInput.HOLD, callback=hold),
}

scanner = Keys([SW_PIN], value_when_pressed=False)
button_config = ButtonInitConfig(
    BUTTON_ENABLE_DOUBLE_PRESS,
    BUTTON_SHORT_PRESS_MS,
    BUTTON_LONG_PRESS_MS,
    BUTTON_HOLD_INTERVAL,
)
button_handler = ButtonHandler(scanner.events, actions, 1, {0: button_config})
runtime.apply_mode_led()


def loop():
    global last_position

    current_position = encoder.position
    position_change = current_position - last_position
    if position_change != 0:
        runtime.handle_rotation(position_change)
        log_debug(current_position)
    last_position = current_position

    # Press
    try:
        button_handler.update()
        time.sleep(LOOP_DELAY_SECONDS)
    except Exception as e:
        runtime.handle_operation_error("button_update", e)


if __name__ == "__main__":
    while True:
        # try except just in case there are any errors that might occur for any reason. Make sure it keeps running.
        try:
            loop()
        except Exception as e2:
            runtime.handle_operation_error("main_loop", e2)
