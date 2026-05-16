#!/usr/bin/env python3
"""Convert WAV audio to PRG32 unsigned 8-bit mono sample data."""

from __future__ import annotations

import argparse
from pathlib import Path
import wave


def _read_pcm(path: Path) -> tuple[list[int], int]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())

    if width not in (1, 2):
        raise SystemExit("only 8-bit and 16-bit PCM WAV files are supported")

    out: list[int] = []
    step = channels * width
    for frame in range(0, len(frames), step):
        total = 0
        for channel in range(channels):
            start = frame + channel * width
            raw = frames[start:start + width]
            if width == 1:
                total += (raw[0] - 128) << 8
            else:
                total += int.from_bytes(raw, "little", signed=True)
        out.append(total // channels)
    return out, rate


def _resample(samples: list[int], source_rate: int, target_rate: int) -> list[int]:
    if source_rate == target_rate or not samples:
        return samples
    count = max(1, int(len(samples) * target_rate / source_rate))
    return [
        samples[min(int(i * source_rate / target_rate), len(samples) - 1)]
        for i in range(count)
    ]


def _trim(samples: list[int], threshold: int = 256) -> list[int]:
    first = 0
    last = len(samples)
    while first < last and abs(samples[first]) < threshold:
        first += 1
    while last > first and abs(samples[last - 1]) < threshold:
        last -= 1
    return samples[first:last]


def _normalize(samples: list[int]) -> list[int]:
    peak = max((abs(v) for v in samples), default=0)
    if peak == 0:
        return samples
    return [max(-32768, min(32767, v * 32767 // peak)) for v in samples]


def to_unsigned8(samples: list[int]) -> bytes:
    values = []
    for value in samples:
        value = max(-32768, min(32767, value))
        values.append((value + 32768) >> 8)
    return bytes(values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--rate", type=int, default=22050)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--trim-silence", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args(argv)

    samples, source_rate = _read_pcm(args.input)
    samples = _resample(samples, source_rate, args.rate)
    if args.trim_silence:
        samples = _trim(samples)
    if args.normalize:
        samples = _normalize(samples)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(to_unsigned8(samples))
    print(f"wrote {args.out} samples={len(samples)} rate={args.rate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
