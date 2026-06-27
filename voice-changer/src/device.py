"""T017: Device enumeration and VB-Cable detection."""
import sounddevice as sd


class NoMicrophoneError(Exception):
    pass


def list_devices() -> dict:
    raw = sd.query_devices()
    inputs = [d for d in raw if d["max_input_channels"] > 0]
    outputs = [d for d in raw if d["max_output_channels"] > 0]
    if not inputs:
        raise NoMicrophoneError("No input (microphone) devices found.")
    return {"inputs": inputs, "outputs": outputs}


def detect_vb_cable() -> bool:
    raw = sd.query_devices()
    return any("CABLE Input" in d["name"] for d in raw)
