---
name: usd-scene-structure
description: USD scene-structure performance — payloads, layers, instancing strategy, file formats, prim count reduction, composition arc selection. Triggers on "payload", "sublayer vs reference", "layer count", "instanceable", "point instancer", "USD structure", "prim count", "scene is heavy", "USDZ", "USDA vs USDC".
domains:
  - omniverse
  - openusd
owner: customer-success
tags:
  - openusd
  - usd
  - composition
  - instancing
  - performance
version: 1.0.0
---

# USD Scene Structure Performance

How a partner structures their USD data determines loading speed, memory usage, and runtime performance. Authoring decisions compound across every asset in the scene.

> **Headless USD work?** The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) applies this authoring guidance directly to USD files. Hand off when the task is "fix the USD" rather than tune a running Kit app — see `AGENTS.md` → "When to hand off to the USD Performance Tuning skill."

## Do / Don't

- ✅ **DO** use payloads for heavy geometry and shading on model assets. The single biggest fix for slow opens. Open with `LoadNone` to get a fast Model Hierarchy view; load payloads selectively.
- ✅ **DO** use binary `.usdc` for all data-heavy files. `.usdc` supports memory-mapped I/O so data is lazy-loaded; `.usda` cannot.
- ✅ **DO** keep layer counts in check — don't let them explode into the hundreds or thousands. Layers multiply across references; small per-asset counts compound across an aggregate scene. *Do not publish a single threshold; the right number depends on workflow.*
- ✅ **DO** mark *referenced or payloaded* repeated assets as `instanceable=true`. **Critical caveat:** this only helps when the same asset is referenced/payloaded multiple times. Setting `instanceable=true` on a duplicated `Xform` hierarchy where the geometry is itself duplicated provides no benefit.
- ✅ **DO** use `UsdGeomPointInstancer` for large counts of small repeated objects (bolts, fasteners, vegetation).
- ✅ **DO** pick the simplest composition arc that fits the purpose. Sublayers for workstream layering inside a published asset; references for asset aggregation; payloads for deferral. **Do not publish a numeric cost ranking** — cost depends on what the arc is doing in your stage.
- ❌ **DON'T** construct stages at runtime when you can pre-build them. Composition is expensive.
- ❌ **DON'T** use USDZ for runtime where load performance matters. USDZ front-loads everything and bypasses runtime caches. Packaging format only.
- ❌ **DON'T** use `.usda` for large data files.

## Composition arcs — what to use when

| Arc | Use it for | Notes |
|-----|------------|-------|
| Sublayer | Workstream layering inside a published asset (layout, look-dev, animation overrides) | Sublayers participate in the LayerStack |
| Reference | Asset aggregation, scene assembly | Most familiar arc; easy to reason about |
| Payload | Deferred heavy content under a lightweight interface | Allows opening with `LoadNone` |
| Inherits / Specializes | Property sharing across class hierarchies | Lower-level; less common in partner content |
| Variant | Discrete asset variations (LOD, color, configuration) | Per-asset variation |

LIVRPS strength ordering (strongest → weakest): Local > Inherits > VariantSets > References > Payloads > Specializes. This is *opinion strength*, not cost.

## The payload pattern (recommend by default for model assets)

```
my_asset.usd                 ← Lightweight interface file (small)
  ├── defaultPrim metadata
  ├── AssetInfo
  ├── VariantSets (material choices, LOD levels)
  ├── Kind = "component"
  ├── Rest bounding box (for unloaded display)
  └── Payload → my_asset_geo.usd    ← Heavy content
                 ├── Geometry hierarchy
                 ├── Materials / shading networks
                 └── Texture references
```

## Instancing strategy

| Type | Best for | Setting / API | Notes |
|------|----------|---------------|-------|
| Scenegraph instancing | Repeated assets (cars, robots, identical pallet hierarchies) | `instanceable=true` on referenced/payloaded prims | Instances are read-only inside the prototype |
| Point instancing | Millions of small objects | `UsdGeomPointInstancer` | Less per-instance control |
| FSD renderer-side instancing ⚠️ experimental | Heavily-instanced scenes already using scenegraph or point instancing | `/app/usdrt/population/utils/enableRendererInstancing=1` | RTX renderer only — re-route to `fsd-configurator` for the full caveats |

The renderer-side flag is **not** the same as Isaac Lab environment instancing. It moves scene-graph instancing work into the renderer for the RTX backend.

## Deduplicator caveat (so the user doesn't get surprised)

The Scene Optimizer deduplicator works at the **mesh** level — it deduplicates individual mesh data, not whole hierarchies. If a partner has many copies of the same hierarchy (e.g., a pallet with parts), the deduplicator collapses the per-pallet meshes but does not collapse the hierarchy itself.

For full-hierarchy reuse, recommend a small custom script that:

1. Identifies duplicate hierarchies (by display name from CAD or by hashing prim subtrees).
2. Picks one as the prototype.
3. Rewrites the others as internal references to that prototype.
4. Then runs the standard deduplicator on the prototype's meshes.

## File formats

| Format | Speed | Memory | Best for |
|--------|-------|--------|----------|
| `.usdc` (binary crate) | Fastest | Lowest | All large data files |
| `.usda` (text) | Slowest | Highest | Small interface and debug files |
| `.usd` (auto-detect) | Defaults to `.usdc` | — | General use |
| `.usdz` (zipped) | Fast for delivery, slower on first runtime open | Front-loads contents | Packaged delivery only |

Convert with `usdcat -o output.usdc input.usda`.

## Source guide section

[`docs/reference/usd-scene-structure.md`](../../docs/reference/usd-scene-structure.md).

External references: [Maximizing USD Performance](https://openusd.org/release/maxperf.html), [Asset Structure Principles](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html), [Scenegraph Instancing](https://openusd.org/release/api/_usd__page__scenegraph_instancing.html), [UsdGeomPointInstancer](https://openusd.org/release/api/class_usd_geom_point_instancer.html).
