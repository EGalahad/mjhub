from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from mjhub.types import (
    DEFAULT_MJCF_REVISION,
    HF_MJCF_URI_SCHEME,
    HuggingFaceMjcfRef,
    MjcfReference,
)


def _build_hf_mjcf_reference(
    *,
    repo_id: str,
    path: str,
    revision: str = DEFAULT_MJCF_REVISION,
) -> HuggingFaceMjcfRef:
    return {
        "kind": "huggingface",
        "repo_id": repo_id,
        "path": path,
        "revision": revision,
    }


def _parse_mjcf_reference(mjcf: MjcfReference) -> MjcfReference:
    if isinstance(mjcf, dict):
        return mjcf

    mjcf_str = str(mjcf)
    if not mjcf_str.startswith(HF_MJCF_URI_SCHEME):
        return mjcf

    raw_reference = mjcf_str[len(HF_MJCF_URI_SCHEME) :]
    parts = raw_reference.split("/", 2)
    if len(parts) < 3:
        raise ValueError(
            "Invalid Hugging Face MJCF URI. Expected "
            "'hf://<namespace>/<repo>/<path>' or "
            "'hf://<namespace>/<repo>@<revision>/<path>'."
        )

    namespace = parts[0]
    repo_and_revision = parts[1]
    repo_path = parts[2]
    repo_name, sep, revision = repo_and_revision.partition("@")
    repo_id = f"{namespace}/{repo_name}"
    if not sep:
        revision = DEFAULT_MJCF_REVISION

    if not repo_id or not repo_path:
        raise ValueError(
            "Invalid Hugging Face MJCF URI. repo_id and path must both be non-empty."
        )

    return _build_hf_mjcf_reference(
        repo_id=repo_id,
        path=repo_path,
        revision=revision,
    )


def _resolve_hf_snapshot_path(*, repo_id: str, path: str, revision: str) -> Path:
    snapshot_root = Path(snapshot_download(repo_id=repo_id, revision=revision))
    resolved_path = snapshot_root / path
    if not resolved_path.is_file():
        raise FileNotFoundError(
            f"MJCF path {path!r} was not found in Hugging Face repo "
            f"{repo_id!r} at revision {revision!r}"
        )
    return resolved_path


def _resolve_huggingface_mjcf(reference: HuggingFaceMjcfRef) -> Path:
    return _resolve_hf_snapshot_path(
        repo_id=str(reference["repo_id"]),
        path=str(reference["path"]),
        revision=str(reference.get("revision", DEFAULT_MJCF_REVISION)),
    )


def resolve_mjcf_reference(
    mjcf: MjcfReference,
    *,
    local_root: str | Path | None = None,
) -> Path:
    mjcf = _parse_mjcf_reference(mjcf)

    if isinstance(mjcf, dict):
        if mjcf.get("kind") != "huggingface":
            raise ValueError(f"Unsupported MJCF reference kind: {mjcf.get('kind')!r}")
        return _resolve_huggingface_mjcf(mjcf)

    mjcf_path = Path(mjcf).expanduser()
    if not mjcf_path.is_absolute():
        if local_root is not None:
            mjcf_path = Path(local_root).expanduser().resolve() / mjcf_path
        mjcf_path = mjcf_path.resolve()
    else:
        mjcf_path = mjcf_path.resolve()

    if not mjcf_path.is_file():
        raise FileNotFoundError(f"MJCF not found: {mjcf_path}")
    return mjcf_path
