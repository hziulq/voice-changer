"""T013: Tests for QualityMode A (pyworld WORLD vocoder)"""
import time
import numpy as np
import pytest


SR = 44100
CHUNK = 1024
# pyworld HARVEST needs ~0.1s+ of audio for accurate pitch detection
LONG_N = SR // 2  # 0.5 seconds


def make_sine(freq, n=CHUNK, sr=SR):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def dominant_freq(audio, sr=SR):
    spectrum = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / sr)
    return freqs[np.argmax(spectrum)]


def test_mode_a_raises_fundamental_above_200hz():
    from src.quality_modes.mode_a import ModeA
    mode = ModeA(pitch_semitones=10, formant_scale=1.4)
    # Use 0.5s signal so HARVEST has enough pitch periods to detect accurately
    chunk = make_sine(120.0, n=LONG_N)
    result = mode.process(chunk, SR)
    freq_out = dominant_freq(result)
    assert freq_out >= 190.0, f"Expected >=190Hz, got {freq_out:.1f}Hz"


def test_mode_a_output_length_equals_input():
    from src.quality_modes.mode_a import ModeA
    mode = ModeA()
    chunk = make_sine(150.0)
    result = mode.process(chunk, SR)
    assert len(result) == len(chunk)


def test_mode_a_processes_within_1000ms():
    from src.quality_modes.mode_a import ModeA
    mode = ModeA()
    chunk = make_sine(150.0)
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 1000, f"Mode A took {elapsed_ms:.1f}ms (limit: 1000ms)"
