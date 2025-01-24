import adafruit_rgbled, board, digitalio, storage, time

SW_PIN = board.GP4
RED_LED = board.GP20
GREEN_LED = board.GP19
BLUE_LED = board.GP18

sw = digitalio.DigitalInOut(SW_PIN)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP

led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)
#
# IMPORTANT FOR EDITING THIS SCRIPT
# In CircuitPython 9.0.0 and later, CIRCUITPY also becomes read-write to your program if it is not visible over USB.
# We will disable usb drive in boot.py
# Press down the knob while plugging in to be able to upload the new code to CIRCUITPY.
#
# if CIRCUITPY storage enabled, LED blink RED
#
if sw.value != 0:
    storage.disable_usb_drive()
else:
    led.color = 0xFF0000
    time.sleep(1)
    led.color = 0xFF0000
    time.sleep(1)