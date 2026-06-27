"""T023: Audio pipeline — sounddevice duplex stream, output routing, safe stop."""
import threading
import numpy as np

from src.quality_modes import QualityModeRouter
from src.effects.chain import EffectChain

# Keywords that identify virtual/undesirable devices
_VIRTUAL = ["CABLE", "Steam", "VoiceWave", "Virtual", "EaseUS",
            "Microsoft サウンド マッパー", "プライマリ"]


class AudioPipeline:
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 4096):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.output_mode = "test"
        self._passthrough = False
        self.is_running = False
        self._level = 0.0
        self.quality_mode = QualityModeRouter()
        self.effect_chain = EffectChain()
        self._stream = None
        self._lock = threading.Lock()

    def set_passthrough(self, enabled: bool) -> None:
        self._passthrough = enabled

    def set_output_mode(self, mode: str) -> None:
        if mode not in ("test", "call"):
            raise ValueError(f"Unknown output mode: {mode}")
        self.output_mode = mode
        if self.is_running:
            self.stop()
            self.start()

    def _process(self, chunk: np.ndarray) -> np.ndarray:
        if self._passthrough:
            return chunk
        processed = self.quality_mode.process(chunk, self.sample_rate)
        return self.effect_chain.process(processed)

    def _find_devices(self, sd):
        """Return (input_idx, output_idx).

        Test mode: both None → Windows default (user-controlled via Sound settings).
        Call mode: input=None (default mic), output=CABLE Input (MME).
        sd.Stream requires both devices on the same host API; None uses MME default.
        """
        devices = list(sd.query_devices())

        # Input: physical Realtek mic on MME (avoid virtual/system-mapper devices)
        input_device = None
        for i, d in enumerate(devices):
            if d["hostapi"] == 0 and d["max_input_channels"] > 0:
                name = d["name"]
                if "Realtek" in name and not any(k in name for k in _VIRTUAL):
                    input_device = i
                    print(f"[Pipeline] Input → [{i}] {name}")
                    break
        if input_device is None:
            print("[Pipeline] WARNING: Realtek mic not found, using system default")

        if self.output_mode == "test":
            print("[Pipeline] Test output → Windows default output device")
            return input_device, None

        # Call mode: find CABLE Input on MME
        for i, d in enumerate(devices):
            if d["hostapi"] == 0 and d["max_output_channels"] > 0:
                if "CABLE Input" in d["name"]:
                    print(f"[Pipeline] Call output → [{i}] {d['name']}")
                    return input_device, i

        print("[Pipeline] WARNING: CABLE Input not found on MME, using system default")
        return input_device, None

    def start(self) -> None:
        import sounddevice as sd

        with self._lock:
            if self.is_running:
                return

            input_device, output_device = self._find_devices(sd)
            print(f"[Pipeline] Input device: {input_device}, Output device: {output_device}, SR: {self.sample_rate}")

            pipeline_ref = self

            def _cb(indata, outdata, frames, time_info, status):
                chunk = indata[:, 0].astype(np.float32)
                pipeline_ref._level = float(np.sqrt(np.mean(chunk ** 2)))
                try:
                    processed = pipeline_ref._process(chunk)
                    out = np.clip(processed.astype(np.float32), -1.0, 1.0)
                    if len(out) < frames:
                        out = np.pad(out, (0, frames - len(out)))
                    else:
                        out = out[:frames]
                except Exception as e:
                    print(f"[Pipeline] Callback error: {e}")
                    out = np.zeros(frames, dtype=np.float32)
                outdata[:, 0] = out
                if outdata.shape[1] > 1:
                    outdata[:, 1] = out

            # sd.Stream (duplex): both devices must be same host API (MME here)
            self._stream = sd.Stream(
                device=(input_device, output_device),
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                channels=(1, 2),
                dtype="float32",
                callback=_cb,
            )
            self._stream.start()
            self.is_running = True
            print(f"[Pipeline] Started — mode={self.output_mode}, chunk={self.chunk_size}samples (~{self.chunk_size*1000//self.sample_rate}ms latency)")

    def stop(self) -> None:
        with self._lock:
            self.is_running = False
            self._level = 0.0
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            print("[Pipeline] Stopped")
