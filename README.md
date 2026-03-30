# multimedia-knob

Use a Raspberry Pi Pico as a desktop multimedia knob with three modes:
- media volume and play/pause
- mouse wheel and click
- brightness shortcuts

![knob3.0.png](https://raw.githubusercontent.com/luckkyboy/multimedia-knob/refs/heads/main/pictures/knob3.0.png)

This project is based on [Xitee1/multimedia-knob](https://github.com/Xitee1/multimedia-knob/tree/main) and keeps the original hardware idea while adding long-press mode switching, RGB mode indication, and button-handler support.

## Features

- 3 operating modes with RGB color feedback
- short press, double press, long press, and hold support
- USB HID output for consumer control, keyboard, and mouse
- write-protected default boot flow for safer daily use

## Hardware

- Raspberry Pi Pico
- KY-040 rotary encoder module
- 5050 SMD RGB LED module
- LDT3.0 light guide column 3 mm, 3.0-2.54 mm
- Knob cap with 6 mm D-port

## GPIO wiring

### Rotary encoder

- `CLK_PIN` -> `GP2`
- `DT_PIN` -> `GP3`
- `SW_PIN` -> `GP4`
- `GND` -> `GND`
- `+` -> `3V3(OUT)`

### RGB LED

- `R` -> `GP20`
- `G` -> `GP19`
- `B` -> `GP18`
- `GND` -> `GND`

![gpio.jpeg](https://raw.githubusercontent.com/luckkyboy/multimedia-knob/refs/heads/main/pictures/gpio.jpeg)

## Firmware layout

- `pico/boot.py`: decides whether the CIRCUITPY drive is exposed
- `pico/code.py`: firmware entrypoint and event loop
- `pico/config.py`: pin mapping, LED colors, and timing constants
- `pico/actions.py`: HID actions
- `pico/modes.py`: mode-to-action mapping
- `pico/runtime.py`: mode state, LED updates, and error recovery
- `pico/lib/`: bundled CircuitPython libraries required by the firmware

## Installation

1. Download the Raspberry Pi Pico CircuitPython UF2.
2. This repository includes `uf2/adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.2.uf2`, which matches the currently bundled firmware dependencies.
3. Plug in the Pico while holding the encoder button so the board mounts as a writable drive.
4. Copy the UF2 file to the Pico boot drive.
5. After reboot, copy the contents of the `pico/` directory to the `CIRCUITPY` drive.
6. Replug the Pico and verify the knob starts normally.

## Dependencies

The firmware currently expects CircuitPython 9.2.2 on Raspberry Pi Pico.

Bundled dependencies in `pico/lib/`:
- `adafruit_hid/*`
- `adafruit_rgbled.mpy`
- `button_handler.mpy`

Notes:
- These `.mpy` files are version-sensitive and may need to be replaced if you upgrade CircuitPython.
- `button_handler.mpy` comes from [CircuitPython_Button_Handler](https://github.com/EGJ-Moorington/CircuitPython_Button_Handler).
- The repository stores the `.mpy` files directly so the board can be flashed without an additional dependency download step.

## Boot behavior

- Normal power-up: `CIRCUITPY` is disabled and the knob runs normally.
- Hold the knob button while plugging in: `CIRCUITPY` stays enabled for file updates.
- In write mode, the RGB LED is solid red.

## Default behavior

- Mode 0, blue:
  volume up/down on rotation, play/pause on short press, mute on double press
- Mode 1, magenta:
  mouse wheel on rotation, left click on short press, `COMMAND+L` on double press, then mode advances
- Mode 2, green:
  brightness up/down on rotation, no short-press action, `ENTER` then `9287` then `ENTER` on double press, then mode advances
- Long press:
  advance to the next mode

## Troubleshooting

- The board does not show up as `CIRCUITPY`:
  unplug it, hold the encoder button, and plug it in again
- The knob boots but editing files is not possible:
  you likely started in normal mode, not write mode
- HID behavior is wrong after a CircuitPython upgrade:
  replace the `.mpy` libraries in `pico/lib/` with versions built for the installed CircuitPython release
- Mode 2 behaves unexpectedly on your computer:
  that mode uses a host-specific keyboard sequence and may need customization for your environment

## References

- Original project: [Xitee1/multimedia-knob](https://github.com/Xitee1/multimedia-knob/tree/main)
- Video tutorial: [magi YouTube tutorial](https://www.youtube.com/watch?v=M6K8vwzZrYs)
- 3D print case: [Thingiverse case](https://www.thingiverse.com/thing:4799088)
