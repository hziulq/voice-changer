"""T012: Tests for QualityMode B (pedalboard PitchShift)"""
import time
import numpy as np
import pytest


SR = 44100
CHUNK = 1024
# Pedalboard's phase vocoder needs ~0.1s window; use 1s for reliable frequency detection
LONG_N = SR


def make_sine(freq, n=CHUNK, sr=SR):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def dominant_freq(audio, sr=SR):
    spectrum = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / sr)
    return freqs[np.argmax(spectrum)]


def test_mode_b_pitch_shift_10_semitones_raises_fundamental():
    from src.quality_modes.mode_b import ModeB
    mode = ModeB(pitch_shift_semitones=10)
    freq_in = 200.0
    # Use a 1-second signal so the phase vocoder has enough context
    chunk = make_sine(freq_in, n=LONG_N)
    result = mode.process(chunk, SR)
    freq_out = dominant_freq(result)
    expected = freq_in * (2 ** (10 / 12))
    assert abs(freq_out - expected) / expected < 0.20, f"Expected ~{expected:.1f}Hz, got {freq_out:.1f}Hz"


def test_mode_b_zero_semitones_preserves_audio():
    from src.quality_modes.mode_b import ModeB
    mode = ModeB(pitch_shift_semitones=0)
    chunk = make_sine(300.0)
    result = mode.process(chunk, SR)
    assert len(result) == len(chunk)
    correlation = np.corrcoef(chunk, result)[0, 1]
    assert correlation > 0.9


def test_mode_b_processes_within_50ms():
    from src.quality_modes.mode_b import ModeB
    mode = ModeB()
    chunk = make_sine(200.0)
    t0 = time.perf_counter()
    mode.process(chunk, SR)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 50, f"Mode B took {elapsed_ms:.1f}ms (limit: 50ms)"
