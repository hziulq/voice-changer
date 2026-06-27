"""T032: Tests for RobotVoice effect."""
import numpy as np
import pytest


CHUNK = 1024
SR = 44100


def make_sine(n=CHUNK):
    t = np.arange(n) / SR
    return (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def test_robot_voice_output_differs_from_input():
    from src.effects.robot_voice import RobotVoice
    robot = RobotVoice(enabled=True)
    chunk = make_sine()
    result = robot.process(chunk)
    assert not np.allclose(result, chunk, atol=1e-6)


def test_robot_voice_output_same_length():
    from src.effects.robot_voice import RobotVoice
    robot = RobotVoice(enabled=True)
    chunk = make_sine()
    result = robot.process(chunk)
    assert len(result) == len(chunk)
