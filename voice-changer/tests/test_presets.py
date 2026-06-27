"""T040: Tests for preset save/load/export/import."""
import os
import shutil
import tempfile
import pytest


@pytest.fixture
def preset_dir(tmp_path):
    d = tmp_path / "presets"
    d.mkdir()
    return d


def test_save_and_load_round_trip(preset_dir):
    from src.presets import PresetManager
    pm = PresetManager(presets_dir=str(preset_dir))
    state = {"quality_mode": "B", "pitch_semitones": 10}
    pm.save("test_preset", state)
    loaded = pm.load("test_preset")
    assert loaded == state


def test_load_nonexistent_raises_preset_not_found(preset_dir):
    from src.presets import PresetManager, PresetNotFoundError
    pm = PresetManager(presets_dir=str(preset_dir))
    with pytest.raises(PresetNotFoundError):
        pm.load("does_not_exist")


def test_load_corrupt_yaml_raises_preset_corrupt_error(preset_dir):
    from src.presets import PresetManager, PresetCorruptError
    p = preset_dir / "broken.yaml"
    p.write_text("{this: [is: not: valid yaml")
    pm = PresetManager(presets_dir=str(preset_dir))
    with pytest.raises(PresetCorruptError):
        pm.load("broken")


def test_import_invalid_yaml_raises_preset_invalid_error(preset_dir, tmp_path):
    from src.presets import PresetManager, PresetInvalidError
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("not_a_dict: [1, 2, 3]\nextra: !!python/object/apply:os.system ['echo hacked']")
    pm = PresetManager(presets_dir=str(preset_dir))
    with pytest.raises(PresetInvalidError):
        pm.import_file(str(bad_file))
