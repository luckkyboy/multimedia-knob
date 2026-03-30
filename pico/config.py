try:
    import board
except ImportError:  # pragma: no cover - local test fallback
    board = None


DEBUG = False

TOTAL_MODES = 3

BUTTON_ENABLE_DOUBLE_PRESS = True
BUTTON_SHORT_PRESS_MS = 350
BUTTON_LONG_PRESS_MS = 900
BUTTON_HOLD_INTERVAL = 2

LED_MODE_0 = 0x0000DD
LED_MODE_1 = 0x880033
LED_MODE_2 = 0x008833
LED_ERROR = 0xFF0000

LOOP_DELAY_SECONDS = 0.0025


if board is not None:
    CLK_PIN = board.GP2
    DT_PIN = board.GP3
    SW_PIN = board.GP4
    RED_LED = board.GP20
    GREEN_LED = board.GP19
    BLUE_LED = board.GP18
else:  # pragma: no cover - local test fallback
    CLK_PIN = "GP2"
    DT_PIN = "GP3"
    SW_PIN = "GP4"
    RED_LED = "GP20"
    GREEN_LED = "GP19"
    BLUE_LED = "GP18"
