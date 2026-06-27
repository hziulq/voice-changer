"""T014: Tests for QualityMode C (hybrid PitchShift + light formant)"""
import time
import numpy as np
import pytest


SR = 44100
CHUNK = 1024


def make_sine(freq, n=CHUNK, sr=SR):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def test_mode_c_output_length_equals_input():
    from src.quality_modes.mode_c import ModeC
    mode = ModeC()
    chunk = make_sine(200.0)
    result = mode.process(chunk, SR)
    assert len(result) == len(chunk)


def test_mode_c_processes_within_200ms():
    from src.quality_modes.mode_c import ModeC
    mode = ModeC()
    chunk = make_sine(200.0)
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 200, f"Mode C took {elapsed_ms:.1f}ms (limit: 200ms)"
