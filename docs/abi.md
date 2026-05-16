# PRG32 ABI

PRG32 cartridge programs call framework functions directly through symbols
exported by the resident firmware. The host cartridge builder resolves those
symbols from `/api/runtime` or from the firmware ELF.

## Register Convention

PRG32 follows the standard RISC-V calling convention:

| Register | Purpose |
|---|---|
| `a0`-`a7` | arguments and return values |
| `ra` | return address |
| `sp` | 16-byte aligned stack |
| `t0`-`t6` | caller-saved temporaries |
| `s0`-`s11` | callee-saved values |

Assembly examples save `ra` around C calls and keep stack alignment visible.

## Audio ABI Calls

The audio ABI is the C API exposed to cartridges:

| Symbol | Purpose | Return |
|---|---|---|
| `prg32_audio_init` | initialize mono/stereo runtime | `bool` |
| `prg32_audio_shutdown` | stop audio runtime | none |
| `prg32_audio_get_mode` | return `PRG32_AUDIO_MODE_MONO` or `STEREO` | mode |
| `prg32_audio_play_sample` | play sample centered | channel or negative |
| `prg32_audio_play_sample_pan` | play sample with pan | channel or negative |
| `prg32_audio_stop_channel` | stop one voice | none |
| `prg32_audio_stop_all` | stop all voices | none |
| `prg32_audio_note_on` | start instrument note | none |
| `prg32_audio_note_on_pan` | start instrument note with pan | none |
| `prg32_audio_note_off` | stop note channel | none |
| `prg32_audio_play_track` | start tracker stream | none |
| `prg32_audio_stop_track` | stop tracker stream | none |
| `prg32_audio_set_tempo` | set tracker BPM | none |
| `prg32_audio_set_master_volume` | set global volume | none |
| `prg32_audio_set_channel_volume` | set one voice volume | none |
| `prg32_audio_set_channel_pan` | set one voice pan | none |

Pan uses signed values:

```text
-64 full left, 0 center, +63 full right
```

Mono builds accept pan calls but mix to one output. Stereo-only programs should
check `prg32_audio_get_mode()` before making a wiring assumption.

## Error Values

Audio calls that return `int` use a non-negative channel number for success and
a negative value for failure. Common failure causes:

- audio runtime was not initialized
- sample id is missing
- channel id is outside the configured voice table
- AUDIO block is invalid

## Assembly Example

```asm
    li a0, 0          /* sample id */
    li a1, 255        /* volume */
    li a2, 1024       /* natural pitch */
    call prg32_audio_play_sample
```

For stereo pan:

```asm
    li a0, 0
    li a1, 255
    li a2, 1024
    li a3, -64        /* left */
    call prg32_audio_play_sample_pan
```

## Splash ABI Calls

Splash helpers are exported for cartridges and examples:

| Symbol | Purpose |
|---|---|
| `prg32_splash_draw` | draw a splash/title screen without delaying |
| `prg32_splash_show` | draw, present, and wait for a duration |
| `prg32_splash_show_default` | show the built-in PRG32 startup splash |

`prg32_splash_show` arguments:

| Register | Value |
|---|---|
| `a0` | title C string |
| `a1` | subtitle C string |
| `a2` | duration in milliseconds |
| `a3` | RGB565 background color |
| `a4` | RGB565 foreground color |
| `a5` | RGB565 accent color |

Example:

```asm
    la a0, game_title
    la a1, game_subtitle
    li a2, 900
    li a3, 0x0000
    li a4, 0xffff
    li a5, 0x07ff
    call prg32_splash_show
```
