"""T035: Reverb effect via pedalboard."""
import numpy as np
from pedalboard import Pedalboard, Reverb as PBReverb
from src.effects.base import AudioEffect


class Reverb(AudioEffect):
    def __init__(self, enabled: bool = False, room_size: float = 0.3):
        super().__init__(enabled)
        self._room_size = room_size
        self._board = Pedalboard([PBReverb(room_size=room_size)])

    def process(self, chunk: np.ndarray, sr: int = 44100) -> np.ndarray:
        if not self.enabled:
            return chunk
        audio = chunk.astype(np.float32)
        result = self._board(audio, sr)
        return result.flatten()[:len(chunk)]

    @property
    def params(self) -> dict:
        return {"enabled": self.enabled, "room_size": self._room_size}
