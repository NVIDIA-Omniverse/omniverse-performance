---
name: scene-optimizer-guide
description: Bottleneck-driven Scene Optimizer workflow — operations, performance validators, trade-offs, and when not to merge meshes. Triggers on "Scene Optimizer", "optimize scene", "merge meshes", "decimate", "deduplicate", "reduce triangles", "performance validator", "asset validator scene".
domains:
  - omniverse
  - openusd
owner: customer-success
tags:
  - scene-optimizer
  - usd
  - openusd
  - validation
  - performance
version: 1.0.0
---

# Scene Optimizer Guide

Scene Optimizer is the most commonly recommended tool for partners with performance issues. The trick is that it isn't a single recipe — operations apply to specific bottlenecks, and the wrong operation can make things worse.

> **Headless USD work?** The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) can drive much of this headlessly on USD files — an end-to-end, agent-driven pass with before/after profiling. Hand off when the task is "fix the USD" rather than tune a running Kit app — see `AGENTS.md` → "When to hand off to the USD Performance Tuning skill."

> **Scene Optimizer without Kit?** The operations are also available as a standalone, embeddable library in the [`usd-optimize`](https://github.com/NVIDIA-Omniverse/usd-optimize) repo (build-from-source or prebuilt binaries; C++/Python). Caveat: it is not currently accepting contributions and makes no parity guarantee with the in-Kit Scene Optimizer — treat it as the embedding/advanced path, not a drop-in.

## Bottleneck-first decision

Don't run the full stack blindly. Match operations to the actual bottleneck.

```
Bottleneck?
├── MEMORY  → Deduplicate Geometry + Optimize Materials + Hidden Mesh Removal + Decimate
├── FPS     → Merge static meshes (only if NOT already instanced or geo-streamed)
│            + Decimate + Optimize Materials + find/deactivate hidden meshes
├── LOAD-TIME → Same memory ops + Compute extents + Prune empty leaves +
│              fix the source pipeline
└── VISUAL artifacts after opt → Generate Normals + Weld Checker + remove degenerates
```

**Critical:** if the user's scene is already heavily instanced, or uses geometry streaming, **do not recommend Merge Meshes**. Merging undoes both wins.

## Do / Don't

- ✅ **DO** run Performance Validators first — diagnosis before modification.
- ✅ **DO** pick operations based on the actual bottleneck, not blindly.
- ✅ **DO** check Statistics before *and* after. If prim count didn't drop, the operation didn't help on that axis.
- ✅ **DO** iterate — decimation tolerance, clustering size, and merge thresholds need tuning per content type.
- ✅ **DO** push fixes upstream when possible. If validators keep finding the same kinds of waste, the connector or source pipeline is usually the right place to fix it.
- ❌ **DON'T** run Scene Optimizer without a backup. Optimization is destructive.
- ❌ **DON'T** skip the report review. Verify visual quality, especially after decimation.
- ❌ **DON'T** treat Scene Optimizer as a fixed pipeline. The "merge → decimate → dedupe materials" sequence is one example, not a prescription.

## Operations reference

| Operation | What it does | Problem solved | Trade-offs |
|-----------|-------------|----------------|------------|
| Merge Meshes | Combines objects (shared material or spatial cluster) | Too many draw calls / prims | Reduces editability; counter-productive for instanced or geo-streamed scenes |
| Decimate Meshes | Reduces face count (%, tolerance, normal-guided) | Excessive triangles | Quality trade-off |
| Deduplicate Geometry | Replaces duplicate meshes with instance prototypes | Duplicate mesh data | **Mesh-level only** — does not collapse hierarchy duplication |
| Optimize Materials | Deduplicates identical materials | Many redundant materials | Re-binds — verify after |
| Convert to Color | Replace shaders with constant color | Aggressive material reduction | Loses shading detail |
| Prune Leaves | Removes empty `Xform`s and `Scope`s | Hierarchy clutter | Generally safe |
| Generate Normals | Fixes misaligned normals | Rendering artifacts | — |
| Split and Merge | Spatial clustering for oversized meshes | Poor culling efficiency | — |
| Center Pivot | Places transform at bbox center | Object manipulation | — |
| Hidden Mesh Removal | Removes fully occluded internal geometry | Internal CAD geometry waste | Expects sealed exteriors |

## The deduplicator caveat (frequently misunderstood)

The current deduplicator works at the **mesh** level — it collapses individual mesh data, not whole hierarchies. If a partner has 12,000 copies of the same pallet hierarchy, the deduplicator collapses the per-pallet meshes but does **not** collapse the pallet hierarchy itself.

For full-hierarchy reuse, recommend a custom script:

1. Identify duplicate hierarchies (by display name from CAD or by hashing prim subtrees).
2. Pick one as the prototype.
3. Rewrite the others as internal references to that prototype.
4. Then run the standard deduplicator on the prototype's meshes.

## Validators (run first)

| Validator | Auto-fix |
|-----------|----------|
| Normals Alignment | Generate Normals |
| Duplicate Materials | Optimize Materials |
| Empty Leaf Prims | Prune Leaves |
| Degenerate Geometry | Remove degenerates |
| Weld Checker | WeldChecker |
| Duplicate Geometry | Deduplicate Geometry |
| Hidden Meshes | Hidden Mesh Removal |
| High Vertex Count | Decimate Meshes |

## Workflow

1. **Diagnose** — Open Statistics; assess prim count, triangle count, material count.
2. **Configure** — Load a preset JSON matching content type, or build a custom stack. Treat presets as a starting point, not a fixed recipe.
3. **Execute** — Run operations top to bottom.
4. **Review** — Check the report tab; compare Statistics before/after.
5. **Iterate** — Adjust parameters and re-run.
6. **Validate** — Re-run Performance Validators to confirm the issues are gone.

## Source guide section

[`docs/workflows/scene-optimization.md`](../../docs/workflows/scene-optimization.md).

External references: [Scene Optimizer Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html), [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html), [What Options Should I Choose?](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/howto.html).
