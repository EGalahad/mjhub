from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias, TypedDict


DEFAULT_MJCF_REVISION = "main"
DEFAULT_GROUND_RGB = (0.2, 0.3, 0.4)
HF_MJCF_URI_SCHEME = "hf://"


class HuggingFaceMjcfRef(TypedDict, total=False):
    kind: Literal["huggingface"]
    repo_id: str
    path: str
    revision: str


MjcfReference: TypeAlias = str | Path | HuggingFaceMjcfRef
