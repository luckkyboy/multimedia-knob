import time

from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse


class KnobActions:
    def __init__(self, consumer_control, mouse, keyboard):
        self.consumer_control = consumer_control
        self.mouse = mouse
        self.keyboard = keyboard

    def volume_up(self):
        self.consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)

    def volume_down(self):
        self.consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)

    def toggle_mute(self):
        self.consumer_control.send(ConsumerControlCode.MUTE)

    def play_pause(self):
        self.consumer_control.send(ConsumerControlCode.PLAY_PAUSE)

    def mouse_scroll_up(self):
        self.mouse.move(wheel=2)

    def mouse_scroll_down(self):
        self.mouse.move(wheel=-2)

    def mouse_left_click(self):
        self.mouse.click(Mouse.LEFT_BUTTON)

    def brightness_up(self):
        self.consumer_control.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)

    def brightness_down(self):
        self.consumer_control.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)

    # Host-specific behavior preserved from the original implementation.
    def mode_1_double_press(self):
        self.keyboard.press(Keycode.COMMAND, Keycode.L)
        self.keyboard.release_all()

    # Host-specific behavior preserved from the original implementation.
    def mode_2_double_press(self):
        self.keyboard.press(Keycode.ENTER)
        self.keyboard.release_all()
        time.sleep(1)
        self.keyboard.press(
            Keycode.NINE,
            Keycode.TWO,
            Keycode.EIGHT,
            Keycode.SEVEN,
        )
        self.keyboard.release_all()
        self.keyboard.press(Keycode.ENTER)
        self.keyboard.release_all()
