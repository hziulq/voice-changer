"""T030: Tests for NoiseGate effect."""
import numpy as np
import pytest


CHUNK = 1024
SR = 44100


def make_sine(amplitude=0.5, n=CHUNK):
    t = np.arange(n) / SR
    return (amplitude * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def test_noise_gate_below_threshold_outputs_silence():
    from src.effects.noise_gate import NoiseGate
    gate = NoiseGate(enabled=True, threshold_db=-20.0)
    # -60dB signal: amplitude ~0.001
    quiet = make_sine(amplitude=0.001)
    result = gate.process(quiet)
    assert np.max(np.abs(result)) < 0.01


def test_noise_gate_above_threshold_passes_audio():
    from src.effects.noise_gate import NoiseGate
    gate = NoiseGate(enabled=True, threshold_db=-40.0)
    loud = make_sine(amplitude=0.5)
    result = gate.process(loud)
    assert np.max(np.abs(result)) > 0.1


def test_noise_gate_disabled_passes_all_audio():
    from src.effects.noise_gate import NoiseGate
    gate = NoiseGate(enabled=False, threshold_db=-20.0)
    quiet = make_sine(amplitude=0.001)
    result = gate.process(quiet)
    np.testing.assert_array_equal(result, quiet)
