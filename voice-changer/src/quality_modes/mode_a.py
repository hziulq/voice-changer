"""T020: QualityMode A — pyworld WORLD vocoder with crossfade to hide chunk boundaries."""
import numpy as np
import pyworld as pw
from src.quality_modes.base import QualityMode

_FADE = 256  # crossfade length in samples (~6ms @ 44100Hz)


class ModeA(QualityMode):
    def __init__(self, pitch_semitones: float = 10.0, formant_scale: float = 1.2):
        self._pitch_semitones = pitch_semitones
        self._formant_scale = formant_scale
        self._prev_tail: np.ndarray | None = None  # last _FADE samples of prev output

    def _synthesize(self, audio: np.ndarray, sr: int) -> np.ndarray:
        f0, t = pw.harvest(audio, sr)
        sp = pw.cheaptrick(audio, f0, t, sr)
        ap = pw.d4c(audio, f0, t, sr)

        f0_shifted = f0 * (2 ** (self._pitch_semitones / 12.0))

        if self._formant_scale != 1.0:
            interp_freqs = np.linspace(0, sr / 2, sp.shape[1])
            src_freqs    = interp_freqs / self._formant_scale
            sp_shifted   = np.zeros_like(sp)
            for i in range(sp.shape[0]):
                sp_shifted[i] = np.interp(interp_freqs, src_freqs, sp[i],
                                          left=sp[i, 0], right=sp[i, -1])
            sp = sp_shifted

        return pw.synthesize(f0_shifted, sp, ap, sr)

    def process(self, chunk: np.ndarray, sr: int) -> np.ndarray:
        n     = len(chunk)
        synth = self._synthesize(chunk.astype(np.float64), sr)

        out = np.zeros(n, dtype=np.float32)
        out[:min(len(synth), n)] = synth[:n].astype(np.float32)

        # Crossfade at the start to hide the boundary with the previous chunk
        if self._prev_tail is not None:
            fade = min(_FADE, n)
            t = np.linspace(0.0, 1.0, fade, dtype=np.float32)
            out[:fade] = self._prev_tail[:fade] * (1.0 - t) + out[:fade] * t

        self._prev_tail = out[-_FADE:].copy()
        return np.clip(out, -1.0, 1.0)

    @property
    def params(self) -> dict:
        return {"pitch_semitones": self._pitch_semitones, "formant_scale": self._formant_scale}
