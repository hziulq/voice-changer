"""T031: Tests for Reverb effect."""
import numpy as np
import pytest


CHUNK = 1024
SR = 44100


def make_sine(n=CHUNK):
    t = np.arange(n) / SR
    return (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def test_reverb_enabled_output_same_length():
    from src.effects.reverb import Reverb
    reverb = Reverb(enabled=True, room_size=0.3)
    chunk = make_sine()
    result = reverb.process(chunk, SR)
    assert len(result) == len(chunk)


def test_reverb_disabled_passthrough():
    from src.effects.reverb import Reverb
    reverb = Reverb(enabled=False)
    chunk = make_sine()
    result = reverb.process(chunk, SR)
    np.testing.assert_array_equal(result, chunk)
