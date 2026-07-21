---
description: "Bottleneck-driven Scene Optimizer workflow: validators, operations, and trade-offs"
---

# Scene Optimization

Scene Optimizer is the most commonly recommended tool for partners with performance issues. It automates the tedious work of mesh merging, deduplication, decimation, and material optimization. Knowing *which* operations apply to *which* bottleneck is the key — there is no universal "optimize my scene" recipe.

The framing follows a bottleneck-first approach: identify the bottleneck (memory, FPS, load time, visual artifacts), then pick the smallest helpful stack of operations.

:::{seealso} Related agentic skill
Working with an AI agent? The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) can drive much of this headlessly on USD files. See {doc}`/agentic-resources`.

Scene Optimizer is also available **without Kit** as the standalone [`usd-optimize`](https://github.com/NVIDIA-Omniverse/usd-optimize) library (build-from-source or prebuilt binaries; C++/Python). Caveat: it is not currently accepting contributions and makes no parity guarantee with the in-Kit Scene Optimizer — treat it as the embedding/advanced path, not a drop-in replacement.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Run Performance Validators before optimizing
:class: tip

Validators catch normals issues, duplicate materials, empty prims, and degenerate geometry — diagnosis before modification. ([Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html))
:::

:::{admonition} DO: Pick operations based on the actual bottleneck
:class: tip

Don't run the full stack blindly. The decision diagram below is the starting point. ([What Options Should I Choose?](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/howto.html))
:::

:::{admonition} DO: Check Statistics before *and* after optimization
:class: tip

Quantify the improvement on the metric you're targeting. If prim count didn't drop, the operation didn't help on that axis.
:::

:::{admonition} DO: Iterate
:class: tip

Decimation tolerance, clustering size, and merge thresholds all need tuning per content type.
:::

:::{admonition} DO: Push fixes upstream when you can
:class: tip

If Scene Optimizer keeps finding the same kinds of waste — duplicate geometry, duplicate materials, hidden internals — the underlying connector or source pipeline is usually the right place to fix it. Downstream optimization is a workaround, not a substitute for clean source data.
:::

:::{admonition} DON'T: Run Scene Optimizer without a backup
:class: warning

Optimization is destructive. Save or version the scene first.
:::

:::{admonition} DON'T: Skip the review step
:class: warning

Check the report tab for per-operation changes. Verify visual quality, especially after decimation.
:::

:::{admonition} DON'T: Treat Scene Optimizer as a fixed pipeline
:class: warning

A "merge meshes → decimate → dedupe materials" sequence is one example workflow, not a prescription. For properly-instanced CAD or geometry-streamed content, merging meshes is counter-productive.
:::

## Performance validators (run first)

| Validator | Checks for | Auto-fix | Doc |
|-----------|-----------|----------|-----|
| Normals Alignment | Mesh normals vs face orientation | Generate Normals | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Duplicate Materials | Identical materials across stage | Optimize Materials | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Empty Leaf Prims | Empty `Xform`s and `Scope`s | Prune Leaves | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Degenerate Geometry | Prims with 0.0 extent | Remove degenerates | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Weld Checker | Manifold-condition violations | WeldChecker | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Duplicate Geometry | Identical meshes that could be instanced | Deduplicate Geometry | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| Hidden Meshes | Fully occluded internal geometry | Hidden Mesh Removal | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |
| High Vertex Count | Excessively dense meshes | Decimate Meshes | [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html) |

## Decision guide: what problem are you solving?

```{mermaid}
flowchart TD
    start["Scene Optimizer<br/>which operations?"] --> q{"Bottleneck?"}
    q -->|Memory| mem["Deduplicate Geometry<br/>Optimize Materials<br/>Hidden Mesh Removal<br/>Decimate Meshes"]
    q -->|FPS / interactivity| fps["Merge static meshes<br/>(if not already instanced)<br/>Decimate Meshes<br/>Optimize Materials<br/>Find &amp; deactivate hidden meshes"]
    q -->|Load time| load["Same as memory ops<br/>Compute extents if missing<br/>Prune empty leaves<br/>Fix source pipeline"]
    q -->|Visual artifacts after opt| vis["Generate Normals<br/>Weld Checker<br/>Remove degenerates<br/>Review report"]
```

If you find yourself running merge-meshes for "FPS" but your scene is already heavily instanced or uses geometry streaming, stop — merging undoes both of those wins.

## Scene Optimizer operations reference

| Operation | What it does | Problem it solves | Trade-offs | Doc |
|-----------|-------------|-------------------|------------|-----|
| Merge Meshes | Combines objects (shared material or spatial clustering) | Too many draw calls / prims | Reduces editability; counter-productive for instanced or geo-streamed scenes | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Decimate Meshes | Reduces face count (%, tolerance, normal-guided) | Excessive triangles | Quality trade-off | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Deduplicate Geometry | Replaces duplicate meshes with instance prototypes | Duplicate mesh data | Mesh-level only — no hierarchy collapse | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Optimize Materials | Deduplicates identical materials | Many redundant materials | Re-binds — verify after | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Convert to Color | Replace shaders with constant color | Aggressive material reduction | Loses shading detail | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Prune Leaves | Removes empty `Xform`s and `Scope`s | Hierarchy clutter | Generally safe | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Generate Normals | Fixes misaligned normals | Rendering artifacts | — | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Split and Merge | Spatial clustering for oversized meshes | Poor culling efficiency on huge spanning meshes | — | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Center Pivot | Places transform at bounding-box center | Object manipulation | — | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |
| Hidden Mesh Removal | Removes fully occluded internal geometry | Internal CAD geometry waste | Expects sealed exteriors | [Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html) |

## A note on the deduplicator

The current deduplicator works at the *mesh* level — it deduplicates individual mesh data, not whole hierarchies. If you have, say, 12,000 copies of the same pallet hierarchy, the deduplicator will collapse the per-pallet meshes but will not collapse the pallet hierarchy itself, so prim-count savings are limited.

For full-hierarchy reuse, the practical approach today is a small custom script: identify the duplicate hierarchies (by display name from the source CAD or by hashing prim subtrees), pick one as the prototype, and rewrite the others as internal references to that prototype. Then the standard deduplicator can collapse the meshes inside the prototype hierarchy.

A future enhancement that hashes hierarchies and runs deduplication top-down would close this gap; for now, do not assume the deduplicator alone will resolve hierarchy-level duplication.

## Workflow for running Scene Optimizer

1. **Diagnose.** Open Statistics to assess prim count, triangle count, material count.
2. **Configure.** Load a preset JSON matching your content type, or build a custom stack. Treat presets as a starting point, not a fixed recipe.
3. **Execute.** Run operations top-to-bottom.
4. **Review.** Check the report tab for per-operation changes; compare Statistics before/after.
5. **Iterate.** Adjust parameters (decimation tolerance, clustering size) and re-run.
6. **Validate.** Re-run Performance Validators to confirm the issues are gone.
