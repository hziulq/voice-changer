"""T021: QualityMode C — hybrid PitchShift + light formant correction ≤200ms."""
import numpy as np
from pedalboard import Pedalboard, PitchShift
from src.quality_modes.base import QualityMode


class ModeC(QualityMode):
    def __init__(self, pitch_shift_semitones: float = 10.0, formant_scale: float = 1.2):
        self._semitones = pitch_shift_semitones
        self._formant_scale = formant_scale
        self._board = Pedalboard([PitchShift(semitones=pitch_shift_semitones)])

    def process(self, chunk: np.ndarray, sr: int) -> np.ndarray:
        audio = chunk.astype(np.float32)
        pitched = self._board(audio, sr).flatten()[:len(chunk)]

        if self._formant_scale == 1.0:
            return pitched

        # Light spectral tilt correction to approximate formant shift
        n = len(pitched)
        spectrum = np.fft.rfft(pitched, n=n)
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        scale = (freqs / (sr / 2 * self._formant_scale) + 1e-6)
        tilt = np.clip(scale, 0.5, 2.0)
        spectrum_corrected = spectrum * tilt
        result = np.fft.irfft(spectrum_corrected, n=n).astype(np.float32)
        return result

    @property
    def params(self) -> dict:
        return {"pitch_shift_semitones": self._semitones, "formant_scale": self._formant_scale}
