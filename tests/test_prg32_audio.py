from __future__ import annotations

import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audio_model = load_module("prg32_audio_model", ROOT / "tools" / "prg32_audio_model.py")
audio_pack = load_module("prg32audio_pack", ROOT / "tools" / "prg32audio_pack.py")


class AudioPanTests(unittest.TestCase):
    def test_center_pan_sends_full_signal_to_both_channels(self) -> None:
        self.assertEqual(audio_model.pan_left_gain(0), 255)
        self.assertEqual(audio_model.pan_right_gain(0), 255)

    def test_extreme_pan_silences_opposite_channel(self) -> None:
        self.assertEqual(audio_model.pan_left_gain(63), 0)
        self.assertEqual(audio_model.pan_right_gain(-64), 0)


class AudioMixerTests(unittest.TestCase):
    def test_mono_mix_saturates(self) -> None:
        voices = [
            audio_model.Voice(bytes([255]), volume=255),
            audio_model.Voice(bytes([255]), volume=255),
        ]
        self.assertEqual(audio_model.mix_mono(voices, 1), [32767])

    def test_sample_position_stepping(self) -> None:
        voice = audio_model.Voice(bytes([128, 255, 0]), step_fp=1 << 16)
        audio_model.mix_mono([voice], 2)
        self.assertEqual(voice.position_fp, 2 << 16)

    def test_stereo_pan_split(self) -> None:
        left = audio_model.Voice(bytes([255]), pan=-64)
        right = audio_model.Voice(bytes([255]), pan=63)
        mixed = audio_model.mix_stereo([left, right], 1)
        self.assertEqual(mixed[0][0], (255 - 128) << 8)
        self.assertEqual(mixed[0][1], (255 - 128) << 8)


class AudioPackTests(unittest.TestCase):
    def test_audio_pack_header_and_descriptors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "click.raw").write_bytes(bytes([128, 255, 128]))
            config = {
                "samples": [{"file": "click.raw", "base_note": 60}],
                "instruments": [{"sample_id": 0, "default_volume": 200}],
                "tracks": [
                    {
                        "events": [
                            {"delta": 0, "command": "PLAY_SAMPLE", "arg0": 0, "arg1": 255},
                            {"delta": 4, "command": "END"},
                        ]
                    }
                ],
            }
            block = audio_pack.pack_audio(config, tmp_path)

        header = struct.unpack_from("<4sHHHHHHIIIIII", block, 0)
        self.assertEqual(header[0], b"AUD0")
        self.assertEqual(header[3], 1)
        self.assertEqual(header[4], 1)
        self.assertEqual(header[5], 1)
        self.assertEqual(header[-1], len(block))


if __name__ == "__main__":
    unittest.main()
