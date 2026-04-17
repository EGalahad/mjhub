from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias, TypedDict


DEFAULT_ASSET_REVISION = "main"
DEFAULT_MJCF_REVISION = DEFAULT_ASSET_REVISION
DEFAULT_GROUND_RGB = (0.2, 0.3, 0.4)
HF_ASSET_URI_SCHEME = "hf://"
HF_MJCF_URI_SCHEME = HF_ASSET_URI_SCHEME


class HuggingFaceAssetRef(TypedDict, total=False):
    kind: Literal["huggingface"]
    repo_id: str
    path: str
    revision: str


AssetReference: TypeAlias = str | Path | HuggingFaceAssetRef

# Backward-compatible aliases for the original MJCF-specific API.
HuggingFaceMjcfRef = HuggingFaceAssetRef
MjcfReference: TypeAlias = AssetReference
