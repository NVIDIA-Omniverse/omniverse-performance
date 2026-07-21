---
description: "USDRT, Fabric, and Kit-specific USD performance patterns: stage queries, change tracking, runnable code samples"
---

# USD in Kit: USDRT, Fabric & Kit-Specific Patterns

This is the biggest knowledge gap we see with partners. Developers learn USD through "Learn USD" courses, which teach standard traversal and `TfNotice` patterns. These work for small scenes but don't scale. Kit provides faster alternatives — USDRT, Fabric, and `UsdWatcher` — that most developers never discover because they don't know to look for them.

:::{seealso} Related agentic skill
Working with an AI agent? The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) can apply these USDRT/Fabric patterns directly. See {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Use USDRT stage queries instead of Python stage traversal
:class: tip

Traversing large stages in Python is extremely slow and does not scale. USDRT queries are single-call operations optimized for Kit. ([Fast Stage Queries with USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usdrt_query.html))
:::

:::{admonition} DO: Use USDRT change tracking or `UsdWatcher` instead of `TfNotice` callbacks
:class: tip

`TfNotice` fires for *any* change on the stage — even unrelated ones. USDRT change tracking and `UsdWatcher` provide targeted, filtered change notifications. ([Change Tracking in USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/changetracking.html), [`UsdWatcher`](https://docs.omniverse.nvidia.com/kit/docs/omni.usd/latest/omni.usd/omni.usd.UsdWatcher.html))
:::

:::{admonition} DO: Use USDRT/Fabric for runtime use cases that don't need to persist to USD
:class: tip

If you're reading composed data at runtime and don't need to write back to USD layers, USDRT gives you direct Fabric access. ([USD, Fabric, and USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usd_fabric_usdrt.html))
:::

:::{admonition} DO: Consolidate `TfNotice` callbacks if you must use one
:class: tip

A single callback that handles multiple purposes is cheaper than registering many callbacks that each fire on every change.
:::

:::{admonition} DON'T: Traverse the stage in Python to find specific prims
:class: warning

This is the most common runtime performance pitfall we see at scale. Use USDRT stage queries.
:::

:::{admonition} DON'T: Register many `TfNotice` callbacks in Python
:class: warning

Each callback fires for every stage change. Overhead compounds quickly.
:::

:::{admonition} DON'T: Construct stages at runtime when you can pre-build them
:class: warning

Composition is expensive. Load fully configured stages instead.
:::

## The USD → USDRT decision

```
Do I need to persist changes back to USD layers?
│
├── YES → Use standard USD API (Sdf/Usd)
│         But still use USDRT for *reading* where possible
│
└── NO  → Use USDRT / Fabric
          ├── Reading composed prim data → USDRT scenegraph API
          ├── Querying for prims by type/property → USDRT stage queries
          └── Tracking changes → USDRT change tracking
```

## Stage traversal — the anti-pattern and the fix

The slow path traverses every prim in Python. The fast path uses a USDRT stage query that is a single optimized call into Fabric.

### Slow (Python traversal)

```python
import omni.usd
from pxr import Usd, UsdLux

stage: Usd.Stage = omni.usd.get_context().get_stage()
dome_light = None
for prim in stage.Traverse():
    if prim.IsA(UsdLux.DomeLight):
        dome_light = prim
        break
```

This iterates every prim in Python. On a stage with hundreds of thousands of prims this can take many seconds.

### Fast (USDRT stage query)

```python
import omni.usd
import usdrt.Usd

stage_id = omni.usd.get_context().get_stage_id()
fabric_stage = usdrt.Usd.Stage.Attach(stage_id)
dome_lights = fabric_stage.GetPrimsWithTypeName("DomeLight")
```

The query is optimized for Kit and scales to millions of prims. Both snippets above are intentionally complete — paste either into the script editor and they run as-is.

Reference: [Fast Stage Queries with USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usdrt_query.html), [USD, Fabric, and USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usd_fabric_usdrt.html).

## Change tracking — `TfNotice` vs alternatives

| Approach | Fires on | Performance | Best for |
|----------|----------|-------------|----------|
| `TfNotice` | Any stage change | Poor at scale, especially in Python | Legacy code, must-have compatibility |
| USDRT Change Tracking | Targeted attributes/prims (USDRT side) | Good | Tracking USDRT updates |
| `UsdWatcher` | Specific watched paths | Good | Targeted path-based monitoring (C++ under the hood) |

### Minimal example — `TfNotice` (the slow path)

```python
import omni.usd
from pxr import Usd, Tf

stage = omni.usd.get_context().get_stage()

def on_stage_change(notice, sender):
    # Fires on every authored change, even unrelated to what we care about.
    for path in notice.GetResyncedPaths():
        print("resynced:", path)

listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, on_stage_change, stage)
# Hold the listener reference for as long as you want notifications.
```

### Minimal example — USDRT change tracking

```python
import omni.usd
import usdrt.Usd

stage_id = omni.usd.get_context().get_stage_id()
fabric_stage = usdrt.Usd.Stage.Attach(stage_id)

# Tracker lifetime governs which changes are observed.
tracker = usdrt.Usd.ChangeTracker(fabric_stage)
tracker.TrackAttribute("xformOp:translate")

# ... time passes, attributes change in Fabric ...

changed_prims = tracker.GetPrimsWithChanges()
# tracker.ClearChanges() to reset the window before the next sample.
```

### Minimal example — `UsdWatcher` (path-targeted)

```python
import omni.usd
from pxr import Sdf

watcher = omni.usd.get_watcher()

def on_xform_change(stage, prim_path, attr_name, value):
    print(f"{prim_path}.{attr_name} -> {value}")

# Subscribe to a specific attribute on a specific prim.
sub = watcher.subscribe_to_change_info_path(
    Sdf.Path("/World/Robot/Base.xformOp:translate"),
    on_xform_change,
)
# Hold `sub` for the lifetime you want notifications.
```

References: [`UsdWatcher`](https://docs.omniverse.nvidia.com/kit/docs/omni.usd/latest/omni.usd/omni.usd.UsdWatcher.html), [USDRT Change Tracking](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/changetracking.html).

## A note on LLM/agent compatibility

USDRT's API is intentionally pin-compatible with standard USD. This is great for developers migrating code, but it creates a challenge for AI assistants — the two APIs look nearly identical, and it's easy for an LLM to confuse which methods work in which context. When working with AI coding assistants, be explicit about whether you want USD or USDRT code, and verify the imports in any sample they produce.
