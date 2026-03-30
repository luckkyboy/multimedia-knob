import adafruit_rgbled
import board
import digitalio
import storage
import time

try:
    from .boot_logic import should_enable_write_mode, write_mode_indicator_colors
except ImportError:
    from boot_logic import should_enable_write_mode, write_mode_indicator_colors

SW_PIN = board.GP4
RED_LED = board.GP20
GREEN_LED = board.GP19
BLUE_LED = board.GP18

switch = digitalio.DigitalInOut(SW_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)

# Press and hold the encoder button while plugging in to expose CIRCUITPY for edits.
# Otherwise, the USB drive is disabled during normal operation.
if should_enable_write_mode(switch.value):
    for color in write_mode_indicator_colors():
        led.color = color
        time.sleep(1)
else:
    storage.disable_usb_drive()
