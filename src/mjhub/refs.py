from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from mjhub.types import (
    AssetReference,
    DEFAULT_ASSET_REVISION,
    HF_ASSET_URI_SCHEME,
    HuggingFaceAssetRef,
)


def _build_hf_asset_reference(
    *,
    repo_id: str,
    path: str,
    revision: str = DEFAULT_ASSET_REVISION,
) -> HuggingFaceAssetRef:
    return {
        "kind": "huggingface",
        "repo_id": repo_id,
        "path": path,
        "revision": revision,
    }


def _parse_asset_reference(reference: AssetReference) -> AssetReference:
    if isinstance(reference, dict):
        return reference

    reference_str = str(reference)
    if not reference_str.startswith(HF_ASSET_URI_SCHEME):
        return reference

    raw_reference = reference_str[len(HF_ASSET_URI_SCHEME) :]
    parts = raw_reference.split("/", 2)
    if len(parts) < 3:
        raise ValueError(
            "Invalid Hugging Face asset URI. Expected "
            "'hf://<namespace>/<repo>/<path>' or "
            "'hf://<namespace>/<repo>@<revision>/<path>'."
        )

    namespace = parts[0]
    repo_and_revision = parts[1]
    repo_path = parts[2]
    repo_name, sep, revision = repo_and_revision.partition("@")
    repo_id = f"{namespace}/{repo_name}"
    if not sep:
        revision = DEFAULT_ASSET_REVISION

    if not repo_id or not repo_path:
        raise ValueError(
            "Invalid Hugging Face asset URI. repo_id and path must both be non-empty."
        )

    return _build_hf_asset_reference(
        repo_id=repo_id,
        path=repo_path,
        revision=revision,
    )


def _resolve_hf_snapshot_path(*, repo_id: str, path: str, revision: str) -> Path:
    snapshot_root = Path(snapshot_download(repo_id=repo_id, revision=revision))
    resolved_path = snapshot_root / path
    if not resolved_path.is_file():
        raise FileNotFoundError(
            f"Asset path {path!r} was not found in Hugging Face repo "
            f"{repo_id!r} at revision {revision!r}"
        )
    return resolved_path


def _resolve_huggingface_asset(reference: HuggingFaceAssetRef) -> Path:
    return _resolve_hf_snapshot_path(
        repo_id=str(reference["repo_id"]),
        path=str(reference["path"]),
        revision=str(reference.get("revision", DEFAULT_ASSET_REVISION)),
    )


def resolve_asset_reference(
    reference: AssetReference,
    *,
    local_root: str | Path | None = None,
) -> Path:
    reference = _parse_asset_reference(reference)

    if isinstance(reference, dict):
        if reference.get("kind") != "huggingface":
            raise ValueError(f"Unsupported asset reference kind: {reference.get('kind')!r}")
        return _resolve_huggingface_asset(reference)

    asset_path = Path(reference).expanduser()
    if not asset_path.is_absolute():
        if local_root is not None:
            asset_path = Path(local_root).expanduser().resolve() / asset_path
        asset_path = asset_path.absolute()
    else:
        asset_path = asset_path.absolute()

    if not asset_path.is_file():
        raise FileNotFoundError(f"Asset not found: {asset_path}")
    return asset_path


def resolve_mjcf_reference(
    mjcf: AssetReference,
    *,
    local_root: str | Path | None = None,
) -> Path:
    return resolve_asset_reference(mjcf, local_root=local_root)
