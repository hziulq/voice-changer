"""T050: Preset CRUD — save/load/export/import via YAML files."""
import os
import shutil
import yaml


class PresetNotFoundError(Exception):
    pass


class PresetCorruptError(Exception):
    pass


class PresetInvalidError(Exception):
    pass


class PresetManager:
    def __init__(self, presets_dir: str = "presets"):
        self._dir = presets_dir
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self._dir, f"{name}.yaml")

    def save(self, name: str, state: dict) -> None:
        with open(self._path(name), "w") as f:
            yaml.safe_dump(state, f)

    def load(self, name: str) -> dict:
        path = self._path(name)
        if not os.path.exists(path):
            raise PresetNotFoundError(f"Preset '{name}' not found.")
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PresetCorruptError(f"Preset '{name}' is corrupt: {e}")
        if not isinstance(data, dict):
            raise PresetCorruptError(f"Preset '{name}' must be a YAML mapping.")
        return data

    def export(self, name: str, dest_path: str) -> None:
        src = self._path(name)
        if not os.path.exists(src):
            raise PresetNotFoundError(f"Preset '{name}' not found.")
        shutil.copy2(src, dest_path)

    def import_file(self, src_path: str) -> str:
        try:
            with open(src_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PresetInvalidError(f"Invalid YAML: {e}")
        if not isinstance(data, dict):
            raise PresetInvalidError("Preset file must contain a YAML mapping.")
        name = os.path.splitext(os.path.basename(src_path))[0]
        dest = self._path(name)
        shutil.copy2(src_path, dest)
        return name
