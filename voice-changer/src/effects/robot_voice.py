"""T036: Robot voice effect via FFT phase randomization."""
import numpy as np
from src.effects.base import AudioEffect


class RobotVoice(AudioEffect):
    def __init__(self, enabled: bool = False):
        super().__init__(enabled)

    def process(self, chunk: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return chunk
        spectrum = np.fft.rfft(chunk)
        magnitudes = np.abs(spectrum)
        random_phases = np.exp(1j * np.random.uniform(0, 2 * np.pi, len(spectrum)))
        result = np.fft.irfft(magnitudes * random_phases, n=len(chunk))
        return result.astype(np.float32)

    @property
    def params(self) -> dict:
        return {"enabled": self.enabled}
