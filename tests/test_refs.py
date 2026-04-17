from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from mjhub.refs import resolve_asset_reference, resolve_mjcf_reference


class ResolveAssetReferenceTests(unittest.TestCase):
    def test_resolve_asset_reference_uses_local_root_for_relative_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            asset_path = root / "assets" / "robot.urdf"
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_text("<robot/>", encoding="utf-8")

            resolved = resolve_asset_reference("assets/robot.urdf", local_root=root)

            self.assertEqual(resolved, asset_path)

    def test_resolve_asset_reference_supports_hf_uri(self) -> None:
        with TemporaryDirectory() as tmpdir:
            snapshot_root = Path(tmpdir)
            asset_path = snapshot_root / "robots" / "robot.xml"
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_text("<mujoco/>", encoding="utf-8")

            with patch("mjhub.refs.snapshot_download", return_value=str(snapshot_root)) as mocked:
                resolved = resolve_asset_reference("hf://demo/assets@main/robots/robot.xml")

            self.assertEqual(resolved, asset_path)
            mocked.assert_called_once_with(repo_id="demo/assets", revision="main")

    def test_resolve_asset_reference_supports_hf_dict_reference(self) -> None:
        with TemporaryDirectory() as tmpdir:
            snapshot_root = Path(tmpdir)
            asset_path = snapshot_root / "robots" / "robot.urdf"
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_text("<robot/>", encoding="utf-8")

            with patch("mjhub.refs.snapshot_download", return_value=str(snapshot_root)):
                resolved = resolve_asset_reference(
                    {
                        "kind": "huggingface",
                        "repo_id": "demo/assets",
                        "path": "robots/robot.urdf",
                        "revision": "main",
                    }
                )

            self.assertEqual(resolved, asset_path)

    def test_resolve_mjcf_reference_is_backward_compatible_alias(self) -> None:
        with TemporaryDirectory() as tmpdir:
            asset_path = Path(tmpdir) / "robot.xml"
            asset_path.write_text("<mujoco/>", encoding="utf-8")

            resolved = resolve_mjcf_reference(asset_path)

            self.assertEqual(resolved, asset_path)


if __name__ == "__main__":
    unittest.main()
