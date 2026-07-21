---
description: "Scene Optimizer operations reference for the AI skill tree — operations, validators, decision guide"
---

# Scene Optimizer Operations Reference

Source: [Scene Optimizer Operations](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html), [Performance Validators](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/performance-validators.html), [What Options Should I Choose?](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/howto.html).

## Operations

| Operation | Purpose | Problem solved | Trade-offs |
|-----------|---------|---------------|------------|
| Merge Meshes | Combine objects by material or spatial cluster | Too many draw calls / prims | Reduces editability; counter-productive for already-instanced or geometry-streamed scenes |
| Decimate Meshes | Reduce face count (%, tolerance, normal-guided) | Excessive triangles | Quality trade-off |
| Deduplicate Geometry | Replace duplicate meshes with instance prototypes | Duplicate mesh data | Mesh-level only — does not collapse hierarchy duplication |
| Optimize Materials | Deduplicate identical materials | Many redundant materials | Re-binds — verify after |
| Convert to Color | Replace shaders with constant color | Aggressive material reduction | Loses shading detail |
| Prune Leaves | Remove empty `Xform`s and `Scope`s | Hierarchy clutter | Generally safe |
| Generate Normals | Fix misaligned normals | Rendering artifacts | — |
| Split and Merge | Spatial clustering for oversized meshes | Poor culling efficiency on huge spanning meshes | — |
| Center Pivot | Place transform at bbox center | Object manipulation | — |
| Hidden Mesh Removal | Remove fully occluded internal geometry | Hidden CAD geometry | Expects sealed exteriors |

## Bottleneck-driven decision guide

```
MEMORY problem  → Deduplicate Geometry + Optimize Materials + Hidden Mesh Removal + Decimate
FPS problem     → Merge Meshes (only if NOT already instanced or geo-streamed) + Decimate +
                  Optimize Materials + find/deactivate hidden meshes
LOAD-TIME problem → Same memory-reduction ops + Compute extents + Prune empty leaves +
                  consider fixing the source pipeline
VISUAL problem  → Generate Normals + Weld Checker + Remove degenerates + review report
```

## Note on the deduplicator

The current deduplicator works at the *mesh* level — it collapses individual mesh data, not whole hierarchies. For full-hierarchy reuse (e.g., 10,000 copies of the same pallet), the practical workaround today is a small custom script that rewrites duplicates as internal references to a single prototype, then runs the standard deduplicator on the prototype's meshes.

A future enhancement that hashes hierarchies and runs deduplication top-down would close this gap; for now, do not assume the deduplicator alone resolves hierarchy-level duplication.

## Validators (run before operations)

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
