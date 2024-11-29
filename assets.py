from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any

import pyray as ray


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


Assets = AttrDict()


def load(dir: Path) -> None:
    for path in chain(dir.glob("**/*.wav"), dir.glob("**/*.png")):
        keys = path.as_posix().replace(path.suffix, "").split("/")[1:]
        current = Assets
        while len(keys) and (key := keys.pop(0)):
            if not len(keys):
                match path.suffix:
                    case ".wav": current[key.replace("-", "_")] = ray.load_sound(path.as_posix())
                    case ".png": current[key.replace("-", "_")] = ray.load_texture(path.as_posix())
                continue
            current[key] = current.get(key, AttrDict())
            current = current[key]


def unload(store: dict[str, Any] = Assets) -> None:
    for value in store.values():
        if isinstance(value, dict):
            unload(value)
            continue
        match value.__class__.__name__:
            case "Sound": ray.unload_sound(value)
            case "Texture": ray.unload_texture(value)
