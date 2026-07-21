---
description: "USD scene structure performance reference: payloads, layers, instancing, file formats, prim count"
---

# USD Scene Structure

How you structure your USD data determines loading speed, memory usage, and runtime performance. The decisions you make at the authoring stage compound across every asset in your scene.

:::{seealso} Related agentic skill
Working with an AI agent? The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) applies this section's authoring guidance directly. See {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Use payloads for heavy geometry and shading on model assets
:class: tip

Payloads defer the heavy content until needed, which is the single biggest fix for slow opens of large stages. ([Maximizing USD Performance](https://openusd.org/release/maxperf.html), [USD Glossary — Payload](https://openusd.org/release/glossary.html#usdglossary-payload))
:::

:::{admonition} DO: Use binary `.usdc` for all data-heavy files
:class: tip

`.usdc` supports memory-mapped I/O so data is lazy-loaded; `.usda` cannot. ([OpenUSD File Formats](https://docs.nvidia.com/learn-openusd/latest/stage-setting/usd-file-formats.html))
:::

:::{admonition} DO: Keep layer counts in check — don't let them explode into the hundreds or thousands
:class: tip

Layers multiply across references; a small per-asset count compounds across an aggregate scene. We deliberately are not putting a single threshold on this — the right number depends on workflow, but the failure mode (procedurally adding layers over time) is consistent.
:::

:::{admonition} DO: Mark *referenced or payloaded* repeated assets as `instanceable=true`
:class: tip

This only helps when the same asset is referenced or payloaded multiple times. Setting `instanceable=true` on a duplicated `Xform` hierarchy where the geometry is itself duplicated provides no benefit — Scenegraph Instancing collapses identical *referenced* hierarchies, not arbitrary identical contents. The deduplicator in Scene Optimizer operates at the mesh level, not the hierarchy level, so for whole-hierarchy reuse you usually want a small script that rewrites duplicates as references to a single prototype. ([Scenegraph Instancing](https://openusd.org/release/api/_usd__page__scenegraph_instancing.html))
:::

:::{admonition} DO: Use Point Instancers for large counts of small repeated objects
:class: tip

Bolts, fasteners, vegetation — Point Instancers reduce stage complexity and prim count more effectively than authored prim hierarchies. ([UsdGeomPointInstancer](https://openusd.org/release/api/class_usd_geom_point_instancer.html))
:::

:::{admonition} DO: Pick the simplest composition arc that fits the purpose
:class: tip

Use sublayers to organize workstreams within a published asset, references for asset aggregation, payloads where deferral matters, and inherits/specializes/variants for property sharing and discrete variation. We deliberately do not publish a numeric cost ranking between arcs — the cost depends on what the arc is doing in your stage. ([USD Best Practices](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/best-practices.html))
:::

:::{admonition} DON'T: Construct stages at runtime when you can pre-build them
:class: warning

Composition is expensive. Load fully configured stages instead.
:::

:::{admonition} DON'T: Use USDZ for runtime where load performance matters
:class: warning

USDZ front-loads everything and bypasses runtime caches. It's a packaging format, not a working format. Batch and cloud workloads where the per-job load cost is paid once are a separate case — see {doc}`/workflows/cloud-deployment`.
:::

:::{admonition} DON'T: Use `.usda` for large data files
:class: warning

It must be fully parsed on load. Reserve it for small interface or debug files.
:::

## Composition arcs — what to use when

| Arc | Use it for | Notes |
|-----|------------|-------|
| **Sublayer** | Workstream layering inside a published asset (layout, look-dev, animation overrides) | Sublayers participate in the LayerStack; large numbers of layered files compound across references |
| **Reference** | Asset aggregation, scene assembly | Most familiar arc for partners; easy to reason about |
| **Payload** | Deferred heavy content under a lightweight interface | Allows opening a stage with `LoadNone` and selectively loading |
| **Inherits / Specializes** | Property sharing across class hierarchies | Lower-level USD building blocks; less common in partner-authored content |
| **Variant** | Discrete asset variations (LOD, color, configuration) | Per-asset variation; selection lives on the consumer |

**LIVRPS strength ordering** (strongest → weakest): Local > Inherits > VariantSets > References > Payloads > Specializes. This is *opinion strength*, not cost. Reference: [USD glossary](https://openusd.org/release/glossary.html#usdglossary-livrps).

If you are tempted to publish a "sublayer is cheaper than reference" rule of thumb, don't — the cost depends on what the arc is doing in your stage and how much composition it pulls into the LayerStack.

## The payload pattern (critical for large scenes)

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

**Why it works.** Opening with `LoadNone` gives you a fast Model Hierarchy view of the stage; you load payloads selectively or on demand. This enables rapid scene browsing, selective loading, and dramatically reduced memory on initial open. The payoff is even larger when assets live on cloud storage, where each unloaded payload is a network request you didn't make — see {doc}`/workflows/cloud-deployment` for the deployment side.

Doc references: [Asset Structure Principles](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html), [Modularity and Content Reuse](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/modularity-guide.html).

## File format quick reference

| Format | Speed | Memory | Best for |
|--------|-------|--------|----------|
| `.usdc` (binary crate) | Fastest | Lowest | All large data files |
| `.usda` (text) | Slowest | Highest | Small interface and debug files |
| `.usd` (auto-detect) | Defaults to `.usdc` | — | General use |
| `.usdz` (zipped) | Fast for delivery, slower on first runtime open | Front-loads contents | Packaged delivery only |

Convert with `usdcat -o output.usdc input.usda`. Reference: [OpenUSD File Formats](https://docs.nvidia.com/learn-openusd/latest/stage-setting/usd-file-formats.html).

## Prim count reduction techniques

| Technique | Notes | Tools |
|-----------|-------|-------|
| Use `transformable` gprims | Skip parent `Xform` prims that exist only to transform a single mesh | Authoring-time fix |
| Property namespaces instead of organizational prims | Use namespaces on properties rather than wrapping prims | Authoring-time fix |
| Merge static meshes by spatial cluster | Reduces prim count when many small meshes share materials | [Scene Optimizer — Merge Meshes](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Instancing (scenegraph and point) | The largest prim-count lever for repeated content | See the instancing table below |

Where you have a downstream optimization tool (Scene Optimizer), still try to fix the source — repeated CAD exports that produce duplicate hierarchies are better fixed in the connector or upstream tool.

## Instancing strategy decision guide

| Type | Best for | Setting / API | Notes |
|------|----------|---------------|-------|
| Scenegraph instancing | Repeated assets (cars, robots, identical pallet hierarchies) | `instanceable=true` on referenced/payloaded prims | Instances are read-only inside the prototype |
| Point instancing | Millions of small objects (bolts, vegetation, debris) | [`UsdGeomPointInstancer`](https://openusd.org/release/api/class_usd_geom_point_instancer.html) | Less per-instance control |
| FSD renderer-side instancing (experimental) | Heavily-instanced scenes that have already used scenegraph or point instancing | `/app/usdrt/population/utils/enableRendererInstancing=1` ([FSD docs](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)) | RTX renderer only; experimental as of Kit 109 — re-check the docs for the current state |

The renderer-side flag is the one that has caused the most confusion in past reviews — it is **not** the same as Isaac Lab environment instancing. It moves scene-graph instancing work into the renderer for the RTX backend.

## Asset structure patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| Atomic | Self-contained component + payload + variants | FlowerPot, Chair |
| Package | Lightweight assembly composing components | ApartmentBuilding |
| Selector | Placeholder for library completion | StreetLamp variants |
| Aggregate | Pure assembly of references with interface overrides | Factory, Neighborhood |

For deeper guidance see [Asset Structure Principles](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html) and [Data Aggregation Best Practices](https://docs.omniverse.nvidia.com/dang/latest/guide/best-practices.html).

## USD loading mechanisms (working-set management)

| Mechanism | Scope | Best for |
|-----------|-------|----------|
| Layer Muting | Entire layers | Workstream isolation |
| Prim Population Mask | Specific prim paths | Pre-filtering before load |
| Payload Loading | Payloaded prims | Primary working-set mechanism |
| Draw Mode (`GeomModelAPI`) | Per prim (requires `kind`) | LOD visualization |
| Activation | Prim and children | Artist-facing show/hide |
