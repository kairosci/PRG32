"""Small host-side reference model for PRG32 audio unit tests."""

from __future__ import annotations

from dataclasses import dataclass


PAN_LEFT = -64
PAN_RIGHT = 63


def pan_left_gain(pan: int) -> int:
    pan = max(PAN_LEFT, min(PAN_RIGHT, pan))
    if pan <= 0:
        return 255
    return 255 - pan * 255 // PAN_RIGHT


def pan_right_gain(pan: int) -> int:
    pan = max(PAN_LEFT, min(PAN_RIGHT, pan))
    if pan >= 0:
        return 255
    return 255 - (-pan) * 255 // (-PAN_LEFT)


def clamp16(value: int) -> int:
    return max(-32768, min(32767, value))


@dataclass
class Voice:
    sample: bytes
    position_fp: int = 0
    step_fp: int = 1 << 16
    volume: int = 255
    pan: int = 0
    loop: bool = False
    loop_start: int = 0
    loop_end: int = 0
    active: bool = True

    def next_pcm(self) -> int:
        index = self.position_fp >> 16
        if index >= len(self.sample):
            if not self.loop or self.loop_end <= self.loop_start:
                self.active = False
                return 0
            index = self.loop_start
            self.position_fp = index << 16
        value = (self.sample[index] - 128) << 8
        value = value * self.volume // 255
        self.position_fp += self.step_fp
        if self.loop and (self.position_fp >> 16) >= self.loop_end:
            self.position_fp = self.loop_start << 16
        return value


def mix_mono(voices: list[Voice], frames: int) -> list[int]:
    out: list[int] = []
    for _ in range(frames):
        out.append(clamp16(sum(v.next_pcm() for v in voices if v.active)))
    return out


def mix_stereo(voices: list[Voice], frames: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for _ in range(frames):
        left = 0
        right = 0
        for voice in voices:
            if not voice.active:
                continue
            pcm = voice.next_pcm()
            left += pcm * pan_left_gain(voice.pan) // 255
            right += pcm * pan_right_gain(voice.pan) // 255
        out.append((clamp16(left), clamp16(right)))
    return out
