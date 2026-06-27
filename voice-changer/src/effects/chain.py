"""T037: Effect chain — NoiseGate → Reverb → RobotVoice."""
import numpy as np
from src.effects.noise_gate import NoiseGate
from src.effects.reverb import Reverb
from src.effects.robot_voice import RobotVoice


class EffectChain:
    def __init__(self):
        self.noise_gate = NoiseGate()
        self.reverb = Reverb()
        self.robot_voice = RobotVoice()

    def process(self, chunk: np.ndarray, sr: int = 44100) -> np.ndarray:
        chunk = self.noise_gate.process(chunk)
        chunk = self.reverb.process(chunk, sr)
        chunk = self.robot_voice.process(chunk)
        return chunk

    def get_state(self) -> dict:
        return {
            "noise_gate": self.noise_gate.params,
            "reverb": self.reverb.params,
            "robot_voice": self.robot_voice.params,
        }
