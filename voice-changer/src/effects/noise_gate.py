"""T034: RMS-based noise gate."""
import numpy as np
from src.effects.base import AudioEffect


class NoiseGate(AudioEffect):
    def __init__(self, enabled: bool = False, threshold_db: float = -40.0):
        super().__init__(enabled)
        self._threshold_db = threshold_db

    def process(self, chunk: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return chunk
        rms = np.sqrt(np.mean(chunk ** 2))
        if rms < 1e-10:
            return np.zeros_like(chunk)
        rms_db = 20 * np.log10(rms)
        if rms_db < self._threshold_db:
            return np.zeros_like(chunk)
        return chunk

    @property
    def params(self) -> dict:
        return {"enabled": self.enabled, "threshold_db": self._threshold_db}
