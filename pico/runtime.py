try:
    from .config import LED_ERROR, TOTAL_MODES
except ImportError:  # pragma: no cover - CircuitPython root import fallback
    from config import LED_ERROR, TOTAL_MODES


class KnobRuntime:
    def __init__(
        self,
        modes,
        led,
        log_debug=None,
        log_error=None,
        recover_hid=None,
        unhealthy_color=LED_ERROR,
    ):
        self.modes = modes
        self.led = led
        self.log_debug = log_debug or (lambda message: None)
        self.log_error = log_error or (lambda message: None)
        self.recover_hid_callback = recover_hid
        self.unhealthy_color = unhealthy_color
        self.current_mode = 0
        self.last_led_color = None
        self.unhealthy = False

    def current_mode_config(self):
        return self.modes[self.current_mode]

    def apply_mode_led(self):
        color = self.current_mode_config()["led_color"]
        if color != self.last_led_color:
            self.led.color = color
            self.last_led_color = color

    def advance_mode(self):
        self.current_mode = (self.current_mode + 1) % TOTAL_MODES
        self.log_debug("Knob Mode: " + str(self.current_mode))
        self.apply_mode_led()

    def handle_rotation(self, delta):
        if delta == 0:
            return

        mode = self.current_mode_config()
        self.log_debug("Knob: turned, mode = " + str(self.current_mode))

        if delta > 0:
            for _ in range(delta):
                mode["on_cw"]()
        else:
            for _ in range(-delta):
                mode["on_ccw"]()

    def handle_short_press(self):
        self.log_debug("Knob: short press detected, mode = " + str(self.current_mode))
        self.current_mode_config()["on_short_press"]()

    def handle_double_press(self):
        self.current_mode_config()["on_double_press"]()

    def handle_hold(self):
        self.log_debug("Knob: hold detected, mode = " + str(self.current_mode))

    def mark_unhealthy(self):
        self.unhealthy = True
        if self.unhealthy_color != self.last_led_color:
            self.led.color = self.unhealthy_color
            self.last_led_color = self.unhealthy_color

    def recover_hid(self, force=False):
        if self.recover_hid_callback is None:
            return
        self.recover_hid_callback(force=force)
        self.unhealthy = False
        self.apply_mode_led()

    def handle_operation_error(self, context, error):
        self.log_error(
            "{} failed in mode {}: {}".format(
                context,
                self.current_mode,
                error,
            )
        )
        try:
            self.recover_hid(force=True)
        except Exception as recovery_error:
            self.log_error(
                "hid recovery failed in mode {}: {}".format(
                    self.current_mode,
                    recovery_error,
                )
            )
            self.mark_unhealthy()
