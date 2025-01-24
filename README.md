# multimedia-knob
![knob3.0.png](https://raw.githubusercontent.com/luckkyboy/multimedia-knob/refs/heads/main/pictures/knob3.0.png)

Use the Raspberry Pi Pico as an multimedia knob to control your PC.

As a base of the code, fork from [multimedia-knob](https://github.com/Xitee1/multimedia-knob/tree/main), by [Xitee1](https://github.com/Xitee1).

## Some more little improvements:
- Add button handler library to support double press and hold event
- Add mode changing function through long press
- Add RGB LED, the colors correspond to modes
- Optimized code logic
- --
- CIRCUITPY storage is disabled, this has no impact on code and functionality.
- Press down the knob while plugging in to be able to upload the new code to CIRCUITPY. at the same time, LED blink RED.

## Parts List:
- Raspberry Pi Pico
- ky-040 rotary encoder module
- 5050 SMD RGB LED module
- LDT3.0 Light guide column 3mm, specification: 3.0-2.54mm
- Knob cap, specification: diameter=30mm~40mm,height=10mm,bore diameter=6mm and D-port

## Connect to GPIO
### Rotary encoder module
- CLK_PIN -> GP2
- DT_PIN -> GP3
- SW_PIN -> GP4
- GND -> GND
- '+ port' -> 3V3(OUT)
### RGB LED module
- R -> GP20
- G -> GP19
- B -> GP18
- GND -> GND
### GPIO
![gpio.jpeg](https://raw.githubusercontent.com/luckkyboy/multimedia-knob/refs/heads/main/pictures/gpio.jpeg)

## How to use it:
1. Download the [CircuitPython UF2 file](https://circuitpython.org/board/raspberry_pi_pico/)
2. Plug in the Pi Pico while holding the bootload button
3. The Pico mounts as storage device on you PC
4. Copy the UF2 file in the root directory of the Pico
5. The Pico will install CircuitPython and then automatically reboot
6. After reboot, you should see a storage device called "CIRCUITPY"
7. Copy all files of the "pico" directory on github into that storage device
8. Re-plug the Pi and try if it works

You can also watch [this Tutorial](https://www.youtube.com/watch?v=M6K8vwzZrYs). It is also made by the original creator of this program (GH: [maxmacstn](https://gist.github.com/maxmacstn) / YT: [magi](https://www.youtube.com/@magichannel)).

## 3D print case
The original creator of this script also made [this case](https://www.thingiverse.com/thing:4799088) for it.
