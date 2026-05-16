# PRG32 Hardware

This page summarizes the classroom reference wiring. See `hardware/README.md`
for the hardware directory map and board scaffolds.

## Base Hardware

| Quantity | Item | Purpose |
|---:|---|---|
| 1 | ESP32-C6 development board | PRG32 RISC-V host |
| 1 | ILI9341 SPI TFT or supported display | video output |
| 1 | digital joystick module | player 1 input |
| 1 | setup button | Wi-Fi setup mode |
| 1 | optional second joystick | player 2 games |

## Mono Audio

| ESP32-C6 | MAX98357A |
|---|---|
| 3V3 or 5V | VIN |
| GND | GND |
| GPIO4 | BCLK |
| GPIO5 | LRC / WS |
| GPIO6 | DIN |
| GPIO7 optional | SD |

Connect one 4-8 ohm speaker to the MAX98357A speaker `+` and `-` outputs.

## Stereo Audio

Stereo uses two MAX98357A boards on the same I2S bus:

| ESP32-C6 | Left MAX98357A | Right MAX98357A |
|---|---|---|
| 3V3 or 5V | VIN | VIN |
| GND | GND | GND |
| GPIO4 | BCLK | BCLK |
| GPIO5 | LRC / WS | LRC / WS |
| GPIO6 | DIN | DIN |
| GPIO7 optional | SD | SD |

Configure the left board for left output and the right board for right output.
Breakout pin labels vary; verify the vendor pinout before soldering.

## Safety Notes

- Do not connect speaker outputs to headphones or line inputs.
- Keep speaker wires short during breadboard tests.
- Use a power source that can supply the speaker current.
- Reassign audio GPIOs if they conflict with the display or joystick wiring in
  a specific classroom kit.
