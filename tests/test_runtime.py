import unittest

from pico.modes import build_modes
from pico.runtime import KnobRuntime


class FakeActions:
    def __init__(self):
        self.calls = []

    def volume_up(self):
        self.calls.append("volume_up")

    def volume_down(self):
        self.calls.append("volume_down")

    def toggle_mute(self):
        self.calls.append("toggle_mute")

    def play_pause(self):
        self.calls.append("play_pause")

    def mouse_scroll_up(self):
        self.calls.append("mouse_scroll_up")

    def mouse_scroll_down(self):
        self.calls.append("mouse_scroll_down")

    def mouse_left_click(self):
        self.calls.append("mouse_left_click")

    def brightness_up(self):
        self.calls.append("brightness_up")

    def brightness_down(self):
        self.calls.append("brightness_down")

    def mode_1_double_press(self):
        self.calls.append("mode_1_double_press")

    def mode_2_double_press(self):
        self.calls.append("mode_2_double_press")


class FakeLed:
    def __init__(self):
        self.colors = []

    @property
    def color(self):
        if not self.colors:
            return None
        return self.colors[-1]

    @color.setter
    def color(self, value):
        self.colors.append(value)


class KnobRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.actions = FakeActions()
        self.led = FakeLed()
        self.debug_logs = []
        self.error_logs = []
        self.recovery_calls = []
        self.runtime = KnobRuntime(
            build_modes(self.actions),
            self.led,
            log_debug=self.debug_logs.append,
            log_error=self.error_logs.append,
            recover_hid=self._recover_hid,
        )

    def _recover_hid(self, force=False):
        self.recovery_calls.append(force)

    def test_mode_zero_actions_match_existing_behavior(self):
        self.runtime.handle_rotation(1)
        self.runtime.handle_rotation(-1)
        self.runtime.handle_short_press()
        self.runtime.handle_double_press()

        self.assertEqual(
            ["volume_up", "volume_down", "play_pause", "toggle_mute"],
            self.actions.calls,
        )

    def test_long_press_cycles_modes(self):
        self.runtime.advance_mode()
        self.runtime.advance_mode()
        self.runtime.advance_mode()

        self.assertEqual(0, self.runtime.current_mode)

    def test_mode_specific_actions_follow_original_mapping(self):
        self.runtime.advance_mode()
        self.runtime.handle_rotation(1)
        self.runtime.handle_rotation(-1)
        self.runtime.handle_short_press()
        self.runtime.handle_double_press()

        self.runtime.advance_mode()
        self.runtime.handle_rotation(1)
        self.runtime.handle_rotation(-1)
        self.runtime.handle_short_press()
        self.runtime.handle_double_press()

        self.assertEqual(
            [
                "mouse_scroll_down",
                "mouse_scroll_up",
                "mouse_left_click",
                "mode_1_double_press",
                "brightness_up",
                "brightness_down",
                "mode_2_double_press",
            ],
            self.actions.calls,
        )

    def test_led_updates_when_mode_changes(self):
        self.runtime.apply_mode_led()
        self.runtime.advance_mode()
        self.runtime.advance_mode()

        self.assertEqual([0x0000DD, 0x880033, 0x008833], self.led.colors)

    def test_led_does_not_rewrite_same_color(self):
        self.runtime.apply_mode_led()
        self.runtime.apply_mode_led()

        self.assertEqual([0x0000DD], self.led.colors)

    def test_operation_error_logs_and_recovers(self):
        error = RuntimeError("button update failed")

        self.runtime.handle_operation_error("button_update", error)

        self.assertEqual([True], self.recovery_calls)
        self.assertEqual(
            ["button_update failed in mode 0: button update failed"],
            self.error_logs,
        )

    def test_recovery_failure_marks_runtime_unhealthy(self):
        def failing_recover(force=False):
            raise RuntimeError("hid init failed")

        runtime = KnobRuntime(
            build_modes(self.actions),
            self.led,
            log_error=self.error_logs.append,
            recover_hid=failing_recover,
            unhealthy_color=0xFF0000,
        )

        runtime.handle_operation_error("main_loop", RuntimeError("loop failed"))

        self.assertTrue(runtime.unhealthy)
        self.assertEqual(0xFF0000, self.led.color)
        self.assertEqual(
            [
                "main_loop failed in mode 0: loop failed",
                "hid recovery failed in mode 0: hid init failed",
            ],
            self.error_logs,
        )


if __name__ == "__main__":
    unittest.main()
