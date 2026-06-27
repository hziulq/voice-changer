"""T018: Abstract base class for quality modes."""
from abc import ABC, abstractmethod
import numpy as np


class QualityMode(ABC):
    @abstractmethod
    def process(self, chunk: np.ndarray, sr: int) -> np.ndarray:
        ...

    @property
    @abstractmethod
    def params(self) -> dict:
        ...
