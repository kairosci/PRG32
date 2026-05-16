#!/usr/bin/env python3
"""Convert simple MIDI note data to PRG32 tracker JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def midi_to_events(path: Path, ticks_per_beat: int = 24) -> list[dict[str, int | str]]:
    try:
        import mido
    except ImportError as exc:
        raise SystemExit("MIDI conversion requires mido: python3 -m pip install mido") from exc

    midi = mido.MidiFile(path)
    events: list[dict[str, int | str]] = []
    elapsed_ticks = 0
    tempo = 500000
    for msg in midi:
        elapsed_ticks += int(mido.second2tick(msg.time, midi.ticks_per_beat, tempo))
        delta = max(0, elapsed_ticks * ticks_per_beat // midi.ticks_per_beat)
        elapsed_ticks = 0
        if msg.type == "set_tempo":
            tempo = msg.tempo
            bpm = int(round(mido.tempo2bpm(tempo)))
            events.append({"delta": delta, "command": "SET_TEMPO", "arg0": bpm, "arg1": 0})
        elif msg.type == "note_on" and msg.velocity > 0:
            channel = getattr(msg, "channel", 0) & 0x0f
            events.append({"delta": delta, "command": "NOTE_ON", "arg0": channel, "arg1": msg.note})
        elif msg.type in ("note_off", "note_on"):
            channel = getattr(msg, "channel", 0) & 0x0f
            events.append({"delta": delta, "command": "NOTE_OFF", "arg0": channel, "arg1": 0})
    events.append({"delta": 0, "command": "END", "arg0": 0, "arg1": 0})
    return events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ticks-per-beat", type=int, default=24)
    args = parser.parse_args(argv)

    document = {"tracks": [{"name": args.input.stem, "events": midi_to_events(args.input, args.ticks_per_beat)}]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
