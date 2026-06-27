"""T010: Tests for device.py — list_devices, detect_vb_cable, NoMicrophoneError"""
import pytest
from unittest.mock import patch


def test_list_devices_returns_nonempty_list():
    fake_devices = [
        {"name": "Microphone (USB)", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("sounddevice.query_devices", return_value=fake_devices):
        from src.device import list_devices
        result = list_devices()
    assert isinstance(result, dict)
    assert "inputs" in result
    assert "outputs" in result
    assert len(result["inputs"]) > 0 or len(result["outputs"]) > 0


def test_detect_vb_cable_returns_false_when_absent():
    fake_devices = [
        {"name": "Microphone (USB)", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("sounddevice.query_devices", return_value=fake_devices):
        from src.device import detect_vb_cable
        result = detect_vb_cable()
    assert result is False


def test_detect_vb_cable_returns_true_when_present():
    fake_devices = [
        {"name": "CABLE Input (VB-Audio Virtual Cable)", "max_input_channels": 0, "max_output_channels": 2},
        {"name": "Microphone (USB)", "max_input_channels": 2, "max_output_channels": 0},
    ]
    with patch("sounddevice.query_devices", return_value=fake_devices):
        from src.device import detect_vb_cable
        result = detect_vb_cable()
    assert result is True


def test_no_microphone_error_raised_when_no_input():
    fake_devices = [
        {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("sounddevice.query_devices", return_value=fake_devices):
        from src.device import list_devices, NoMicrophoneError
        with pytest.raises(NoMicrophoneError):
            list_devices()
