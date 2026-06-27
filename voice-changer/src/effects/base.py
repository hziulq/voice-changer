"""T033: Abstract base class for audio effects."""
from abc import ABC, abstractmethod
import numpy as np


class AudioEffect(ABC):
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    @abstractmethod
    def process(self, chunk: np.ndarray) -> np.ndarray:
        ...

    @property
    @abstractmethod
    def params(self) -> dict:
        ...
