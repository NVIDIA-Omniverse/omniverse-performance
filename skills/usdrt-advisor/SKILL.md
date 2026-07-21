---
name: usdrt-advisor
description: Migrate Kit code from Python USD traversal to USDRT stage queries, and from TfNotice callbacks to USDRT change tracking or UsdWatcher. Triggers on "USDRT", "Fabric", "stage traversal slow", "TfNotice", "stage query", "change tracking", "UsdWatcher", "Python performance in Kit". Provides complete runnable code samples.
domains:
  - omniverse
  - openusd
owner: customer-success
tags:
  - openusd
  - usd
  - usdrt
  - fabric
  - kit
version: 1.0.0
---

# USDRT Advisor

The biggest knowledge gap we see with Kit developers. They learn USD through "Learn USD" courses, which teach standard traversal and `TfNotice` patterns. Those work for small scenes but don't scale. Kit provides faster alternatives — USDRT, Fabric, and `UsdWatcher` — that most developers never discover.

> **Headless USD work?** The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) can apply these USDRT/Fabric patterns directly to USD files. Hand off when the task is "fix the USD" rather than tune a running Kit app — see `AGENTS.md` → "When to hand off to the USD Performance Tuning skill."

## The decision

```
Do I need to persist changes back to USD layers?
├── YES → Use standard USD API (Sdf/Usd)
│         But still use USDRT for *reading* where possible
└── NO  → Use USDRT / Fabric
          ├── Reading composed prim data    → USDRT scenegraph API
          ├── Querying for prims by type    → USDRT stage queries
          └── Tracking changes              → USDRT change tracking
```

## Do / Don't

- ✅ **DO** use USDRT stage queries instead of Python stage traversal. Single-call operations optimized for Kit; scale to millions of prims.
- ✅ **DO** use USDRT change tracking or `UsdWatcher` instead of `TfNotice`. `TfNotice` fires for *any* change; the alternatives are targeted.
- ✅ **DO** consolidate `TfNotice` callbacks if you must use one. A single callback handling multiple purposes is cheaper than registering many.
- ❌ **DON'T** traverse the stage in Python to find specific prims. The most common runtime performance pitfall at scale.
- ❌ **DON'T** register many `TfNotice` callbacks in Python. Overhead compounds quickly.
- ❌ **DON'T** construct stages at runtime when you can pre-build them.

## Stage traversal — anti-pattern and fix

These snippets are intentionally complete, including all imports — paste into the script editor and they run as-is.

### ❌ Slow (Python traversal)

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

On a stage with hundreds of thousands of prims this can take many seconds.

### ✅ Fast (USDRT stage query)

```python
import omni.usd
import usdrt.Usd

stage_id = omni.usd.get_context().get_stage_id()
fabric_stage = usdrt.Usd.Stage.Attach(stage_id)
dome_lights = fabric_stage.GetPrimsWithTypeName("DomeLight")
```

The `Stage.Attach` line is the part that's commonly missing from USDRT documentation samples — include it in any code sample produced for the user.

## Change tracking — three approaches

| Approach | Fires on | Performance | Best for |
|----------|----------|-------------|----------|
| `TfNotice` | Any stage change | Poor at scale, especially in Python | Legacy code, must-have compatibility |
| USDRT change tracking | Targeted attributes/prims (USDRT side) | Good | Tracking USDRT updates |
| `UsdWatcher` | Specific watched paths | Good | Targeted path-based monitoring (C++ under the hood) |

### ⚠️ Slow path — `TfNotice`

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

### ✅ USDRT change tracking

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

### ✅ `UsdWatcher` (path-targeted)

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

## A note on LLM/agent compatibility

USDRT's API is intentionally pin-compatible with standard USD. This is great for migrating code, but it creates a challenge for AI assistants — the two APIs look nearly identical and it's easy to confuse which methods work in which context. **Always be explicit about USD vs USDRT in code samples, and always include the imports.**

## Source guide section

[`docs/reference/usd-in-kit.md`](../../docs/reference/usd-in-kit.md).

External references: [USD, Fabric, and USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usd_fabric_usdrt.html), [Fast Stage Queries with USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usdrt_query.html), [USDRT Change Tracking](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/changetracking.html), [UsdWatcher](https://docs.omniverse.nvidia.com/kit/docs/omni.usd/latest/omni.usd/omni.usd.UsdWatcher.html).
