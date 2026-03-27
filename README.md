# mjhub

`mjhub` is the shared MuJoCo asset-loading layer for this workspace.

It is intentionally small. The first version only owns four concerns:

- declare MJCF references, including Hugging Face-backed assets
- resolve an MJCF reference to a local XML path
- patch a robot-only MJCF into a viewer/sim scene with a floor

## Why this package exists

The same functionality currently appears in several places:

- `any4hdmi/src/any4hdmi/format.py`
- `sim2real/sim2real/utils/mjcf.py`
- `sim2real/sim2real/teleop/mujoco_viewer_utils.py`
- `active-adaptation/projects/hdmi/hdmi/tasks/motion.py`

Those implementations mostly differ in packaging, not intent. `mjhub` is the
shared home for the common logic.

## Public API

```python
from mjhub import (
    HuggingFaceMjcfRef,
    MjcfReference,
    resolve_mjcf_reference,
    temp_mjcf_with_floor,
)
```

### Example

```python
from mjhub import resolve_mjcf_reference

mjcf = "hf://elijahgalahad/g1_xmls@main/g1-mjlab.xml"

mjcf_path = resolve_mjcf_reference(mjcf)
```

You can also pass a compact string reference directly:

```python
from mjhub import temp_mjcf_with_floor

with temp_mjcf_with_floor("path/to/robot.xml") as scene_mjcf_path:
    ...
```

`MjcfReference` intentionally accepts either:

- a local filesystem path
- a `hf://<namespace>/<repo>@<revision>/<path>` string
- a `HuggingFaceMjcfRef` typed dict

## Initial migration targets

- `any4hdmi.format.build_hf_mjcf_reference`
- `any4hdmi.format.resolve_mjcf_reference`
- `sim2real.utils.mjcf.*`
- `sim2real.teleop.mujoco_viewer_utils.*`
- `active-adaptation.projects.hdmi.hdmi.tasks.motion._resolve_any4hdmi_mjcf_path`

Dataset manifests, motion metadata, and project-specific robot config remain
outside `mjhub`.
