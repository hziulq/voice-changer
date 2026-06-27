from src.quality_modes.base import QualityMode
from src.quality_modes.mode_a import ModeA
from src.quality_modes.mode_b import ModeB
from src.quality_modes.mode_c import ModeC


class QualityModeRouter:
    _modes = {"A": ModeA, "B": ModeB, "C": ModeC}

    def __init__(self, mode: str = "B"):
        self._current_key = mode
        self._instance: QualityMode = self._modes[mode]()

    @property
    def current_mode(self) -> str:
        return self._current_key

    def set_mode(self, mode: str) -> None:
        if mode not in self._modes:
            raise ValueError(f"Unknown mode: {mode}. Must be A, B, or C.")
        if mode != self._current_key:
            self._current_key = mode
            self._instance = self._modes[mode]()

    def process(self, chunk, sr: int):
        return self._instance.process(chunk, sr)

    def set_params(self, params: dict) -> None:
        for k, v in params.items():
            attr = f"_{k}"
            if hasattr(self._instance, attr):
                setattr(self._instance, attr, type(getattr(self._instance, attr))(v))

    def get_params(self) -> dict:
        return self._instance.params
