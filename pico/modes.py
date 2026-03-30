try:
    from .config import LED_MODE_0, LED_MODE_1, LED_MODE_2
except ImportError:  # pragma: no cover - CircuitPython root import fallback
    from config import LED_MODE_0, LED_MODE_1, LED_MODE_2


def _noop():
    return None


def build_modes(actions):
    return (
        {
            "name": "volume",
            "led_color": LED_MODE_0,
            "on_cw": actions.volume_up,
            "on_ccw": actions.volume_down,
            "on_short_press": actions.play_pause,
            "on_double_press": actions.toggle_mute,
        },
        {
            "name": "mouse",
            "led_color": LED_MODE_1,
            "on_cw": actions.mouse_scroll_down,
            "on_ccw": actions.mouse_scroll_up,
            "on_short_press": actions.mouse_left_click,
            "on_double_press": actions.mode_1_double_press,
        },
        {
            "name": "brightness",
            "led_color": LED_MODE_2,
            "on_cw": actions.brightness_up,
            "on_ccw": actions.brightness_down,
            "on_short_press": _noop,
            "on_double_press": actions.mode_2_double_press,
        },
    )
