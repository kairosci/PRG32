#!/usr/bin/env python3
"""Pack PRG32 samples, instruments, and tracker events into an AUDIO block."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct


AUDIO_MAGIC = b"AUD0"
AUDIO_VERSION = 1
HEADER = struct.Struct("<4sHHHHHHIIIIII")
SAMPLE_DESC = struct.Struct("<IIIIHBB")
INSTRUMENT_DESC = struct.Struct("<HBBBBBB")
TRACK_DESC = struct.Struct("<II")
EVENT = struct.Struct("<BBBB")

COMMANDS = {
    "NOTE_ON": 1,
    "NOTE_OFF": 2,
    "SET_VOLUME": 3,
    "SET_PAN": 4,
    "SET_TEMPO": 5,
    "PLAY_SAMPLE": 6,
    "JUMP": 7,
    "END": 255,
}


def _align4(data: bytearray) -> None:
    while len(data) % 4:
        data.append(0)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"failed to read {path}: {exc}") from exc


def _command(value: str | int) -> int:
    if isinstance(value, int):
        return value
    try:
        return COMMANDS[value.upper()]
    except KeyError as exc:
        raise SystemExit(f"unknown audio command: {value}") from exc


def pack_audio(config: dict, base_dir: Path) -> bytes:
    samples_cfg = config.get("samples", [])
    instruments_cfg = config.get("instruments", [])
    tracks_cfg = config.get("tracks", [])

    sample_payload = bytearray()
    sample_descs = bytearray()
    for sample in samples_cfg:
        raw_path = base_dir / sample["file"]
        raw = raw_path.read_bytes()
        offset = len(sample_payload)
        sample_payload.extend(raw)
        flags = 1 if sample.get("loop", False) else int(sample.get("flags", 0))
        loop_start = int(sample.get("loop_start", 0))
        loop_end = int(sample.get("loop_end", len(raw) if flags else 0))
        sample_descs.extend(SAMPLE_DESC.pack(
            offset,
            len(raw),
            loop_start,
            loop_end,
            int(sample.get("base_note", 60)),
            flags,
            0,
        ))

    instrument_descs = bytearray()
    for instrument in instruments_cfg:
        instrument_descs.extend(INSTRUMENT_DESC.pack(
            int(instrument.get("sample_id", 0)),
            int(instrument.get("default_volume", 255)),
            int(instrument.get("default_pan", 0)) & 0xff,
            int(instrument.get("attack", 0)),
            int(instrument.get("decay", 0)),
            int(instrument.get("sustain", 255)),
            int(instrument.get("release", 0)),
        ))

    event_payload = bytearray()
    track_descs = bytearray()
    for track in tracks_cfg:
        offset = len(event_payload) // EVENT.size
        events = track.get("events", [])
        for event in events:
            event_payload.extend(EVENT.pack(
                int(event.get("delta", event.get("delta_ticks", 0))) & 0xff,
                _command(event.get("command", "END")) & 0xff,
                int(event.get("arg0", 0)) & 0xff,
                int(event.get("arg1", 0)) & 0xff,
            ))
        track_descs.extend(TRACK_DESC.pack(offset, len(events)))

    block = bytearray(b"\0" * HEADER.size)
    samples_offset = len(block)
    block.extend(sample_descs)
    _align4(block)
    instruments_offset = len(block)
    block.extend(instrument_descs)
    _align4(block)
    tracks_offset = len(block)
    block.extend(track_descs)
    _align4(block)
    events_offset = len(block)
    block.extend(event_payload)
    _align4(block)
    data_offset = len(block)
    block.extend(sample_payload)
    _align4(block)

    header = HEADER.pack(
        AUDIO_MAGIC,
        AUDIO_VERSION,
        HEADER.size,
        len(samples_cfg),
        len(instruments_cfg),
        len(tracks_cfg),
        0,
        samples_offset,
        instruments_offset,
        tracks_offset,
        events_offset,
        data_offset,
        len(block),
    )
    block[:HEADER.size] = header
    return bytes(block)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    config = _load_json(args.input)
    block = pack_audio(config, args.input.parent)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(block)
    print(f"wrote {args.out} bytes={len(block)}")
    print(
        "samples={samples} instruments={instruments} tracks={tracks}".format(
            samples=len(config.get("samples", [])),
            instruments=len(config.get("instruments", [])),
            tracks=len(config.get("tracks", [])),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
