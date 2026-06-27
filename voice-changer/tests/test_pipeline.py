"""T011: Tests for pipeline.py — startup, passthrough, stop, output mode, error handling"""
import numpy as np
import pytest
from unittest.mock import MagicMock, patch


CHUNK = 1024
SR = 44100


def make_chunk(n=CHUNK):
    return np.random.randn(n).astype(np.float32)


def test_pipeline_starts_and_stops():
    with patch("sounddevice.InputStream"), patch("sounddevice.OutputStream"):
        from src.pipeline import AudioPipeline
        p = AudioPipeline(sample_rate=SR, chunk_size=CHUNK)
        p.start()
        p.stop()


def test_pipeline_passthrough_passes_audio_unchanged():
    from src.pipeline import AudioPipeline
    p = AudioPipeline(sample_rate=SR, chunk_size=CHUNK)
    p.set_passthrough(True)

    chunk = make_chunk()
    result = p._process(chunk)
    np.testing.assert_array_equal(result, chunk)


def test_pipeline_output_mode_switch():
    from src.pipeline import AudioPipeline
    p = AudioPipeline(sample_rate=SR, chunk_size=CHUNK)
    p.set_output_mode("test")
    assert p.output_mode == "test"
    p.set_output_mode("call")
    assert p.output_mode == "call"


def test_pipeline_callback_exception_causes_safe_stop():
    from src.pipeline import AudioPipeline

    class BrokenMode:
        def process(self, chunk, sr):
            raise RuntimeError("simulated failure")

    p = AudioPipeline(sample_rate=SR, chunk_size=CHUNK)
    p.quality_mode = BrokenMode()

    with patch("sounddevice.InputStream"), patch("sounddevice.OutputStream"):
        p.start()
        chunk = make_chunk()
        p._callback(chunk.reshape(-1, 1), CHUNK, None, None)
        assert p.is_running is False
