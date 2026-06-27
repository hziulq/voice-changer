"""T015: Latency benchmarks for all quality modes"""
import time
import numpy as np
import pytest


SR = 44100
CHUNK = 1024


def make_sine(freq=200.0, n=CHUNK, sr=SR):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def test_mode_a_latency_under_1000ms():
    from src.quality_modes.mode_a import ModeA
    mode = ModeA()
    chunk = make_sine()
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 1000, f"Mode A: {elapsed_ms:.1f}ms (limit: 1000ms)"


def test_mode_b_latency_under_50ms():
    from src.quality_modes.mode_b import ModeB
    mode = ModeB()
    chunk = make_sine()
    # Warm up pedalboard's JIT — steady-state latency is what matters in production
    mode.process(chunk, SR)
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 50, f"Mode B: {elapsed_ms:.1f}ms (limit: 50ms)"


def test_mode_c_latency_under_200ms():
    from src.quality_modes.mode_c import ModeC
    mode = ModeC()
    chunk = make_sine()
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 200, f"Mode C: {elapsed_ms:.1f}ms (limit: 200ms)"
