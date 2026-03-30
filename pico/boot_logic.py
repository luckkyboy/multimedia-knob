WRITE_MODE_LED_COLOR = 0xFF0000


def should_enable_write_mode(button_value):
    return button_value is False


def write_mode_indicator_colors():
    return [WRITE_MODE_LED_COLOR]
