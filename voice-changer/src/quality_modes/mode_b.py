"""T019: QualityMode B — FFT pitch+formant shift, Gaussian envelope smoothing."""
import numpy as np
from src.quality_modes.base import QualityMode


class ModeB(QualityMode):
    def __init__(self, pitch_shift_semitones: float = 10.0, formant_scale: float = 1.3):
        self._semitones     = pitch_shift_semitones
        self._formant_scale = formant_scale
        # Temporal smoothing: carry the spectral envelope across chunks to
        # prevent sudden discontinuities at chunk boundaries.
        self._smooth_env: np.ndarray | None = None

    @staticmethod
    def _gaussian_envelope(mag: np.ndarray, width: int = 80) -> np.ndarray:
        """Gaussian-smoothed spectral envelope — avoids rectangular-window ripple."""
        t = np.linspace(-3.0, 3.0, width, dtype=np.float64)
        kernel = np.exp(-0.5 * t ** 2)
        kernel /= kernel.sum()
        env = np.convolve(mag.astype(np.float64), kernel, mode="same")
        return np.maximum(env, 1e-8).astype(np.float32)

    @staticmethod
    def _interp_bins(src: np.ndarray, ratio: float, n_bins: int) -> np.ndarray:
        src_f = np.arange(n_bins, dtype=np.float64) / ratio
        si    = np.minimum(src_f.astype(int), n_bins - 1)
        sj    = np.minimum(si + 1,            n_bins - 1)
        frac  = src_f - si
        return np.where(src_f < n_bins,
                        (1.0 - frac) * src[si] + frac * src[sj], 0.0)

    def process(self, chunk: np.ndarray, sr: int) -> np.ndarray:
        audio    = chunk.astype(np.float32)
        spectrum = np.fft.rfft(audio)
        n_bins   = len(spectrum)
        mag      = np.abs(spectrum)
        phase    = np.angle(spectrum)

        # Envelope with temporal smoothing (α=0.25 LP across chunks)
        env_now = self._gaussian_envelope(mag)
        if self._smooth_env is None or len(self._smooth_env) != n_bins:
            self._smooth_env = env_now
        else:
            self._smooth_env = 0.25 * env_now + 0.75 * self._smooth_env

        env = self._smooth_env

        # Separate excitation (pitch-carrying) from formant envelope
        excitation  = (mag / env) * np.exp(1j * phase)

        pitch_ratio = 2.0 ** (self._semitones / 12.0)
        pitched_exc = self._interp_bins(excitation, pitch_ratio, n_bins)
        scaled_env  = self._interp_bins(env,        self._formant_scale, n_bins)

        result_spec = pitched_exc * np.maximum(scaled_env, 1e-8)
        result = np.fft.irfft(result_spec, n=len(audio)).astype(np.float32)
        return np.clip(result, -1.0, 1.0)

    @property
    def params(self) -> dict:
        return {"pitch_shift_semitones": self._semitones,
                "formant_scale": self._formant_scale}
