---
description: "Content preparation, validation, CAD import, materials, and physics — preventing performance issues at the source"
---

# Content Preparation

The quality of your input data determines your performance ceiling. CAD imports authored for manufacturing precision, with thousands of duplicate materials and hidden internal geometry, will be slow no matter how well you tune rendering settings. Content conditioning is where the biggest leverage usually lives.

:::{seealso} Related agentic skill
Working with an AI agent? The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) operates on USD files directly. See {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Validate USD assets early and often
:class: tip

Validation surfaces structural and compatibility issues before they cause runtime problems. The simplest tool that fits your need:

- [`usdchecker`](https://openusd.org/release/api/md_pxr_usd_validation_usd_validation__r_e_a_d_m_e.html) for baseline OpenUSD compliance.
- [Omniverse Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html) for richer rules, UI/CLI/Python workflows, and possible auto-fixes.
- [OpenUSD Validation framework](https://docs.nvidia.com/learn-openusd/latest/data-exchange/asset-validation/what-is-asset-validation.html) when you need custom validators or suites.

The Asset Validator also runs standalone, without Kit: `pip install usd-validation-nvidia` ([PyPI](https://pypi.org/project/usd-validation-nvidia/)) is the same engine as a pure-Python package with a CLI (`nvidia_usd_validate`) and Python API — which is what makes the CI/CD wiring below practical. Use `usd-validation-nvidia`; the older `omniverse-asset-validator` package is frozen.

Wire validation into CI/CD so regressions in exchanged USD output are caught at the importer/exporter boundary, not in production.
:::

:::{admonition} DO: Look at your geometry, run validators, then use Scene Optimizer where it applies
:class: tip

Don't run a full optimizer pipeline blindly. Validators tell you what's wrong; the operations in {doc}`scene-optimization` tell you which fixes to apply.
:::

:::{admonition} DO: Use "Import as Reference" for aggregation workflows
:class: tip

Keeps data modular and references the source file rather than embedding it.
:::

:::{admonition} DO: Use primitive colliders instead of mesh colliders for physics
:class: tip

Spheres and boxes are orders of magnitude faster than complex triangle meshes.
:::

:::{admonition} DO: Fix at the source pipeline when you can
:class: tip

If validation or Scene Optimizer keeps finding the same kinds of waste — duplicate materials, hidden internal geometry, redundant hierarchies — the connector or upstream tool is usually the right place to fix it. Downstream optimization is a workaround, not a substitute for clean source data.
:::

:::{admonition} DON'T: Import CAD data and use it as-is
:class: warning

CAD models are authored for manufacturing precision, not real-time rendering.
:::

:::{admonition} DON'T: Add UV coordinates to meshes that don't need textures
:class: warning

Extra UVs cost memory and processing for no visual benefit.
:::

:::{admonition} DON'T: Use mesh colliders when simpler shapes will do
:class: warning

Physics collider performance ranking: primitives → convex → cylinders → mesh.
:::

## CAD data import methods

| Method | When to use | Notes |
|--------|-------------|-------|
| **CAD Converter** ([docs](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.cad/latest/Overview.html)) | Batch / automated conversion | Plan a post-conversion validation and conditioning pass |
| **Direct DCC export** | Direct from authoring tool | Quality depends on the exporter |
| **Import to Stage** | Editing in current session | Embeds data — can bloat the stage |
| **Import as Reference** | Aggregation workflows | Modular, references the source file |

**Memory requirement.** 16 GB minimum for CAD conversion; complex files may need 32 GB.

## Post-import optimization — example workflow

This is *one* example workflow, not a prescription. It works well for raw CAD imports with many parts sharing materials and lots of internal geometry. **It does not apply to content that is already properly instanced or that uses geometry streaming** — merging meshes in those cases is counter-productive.

```
1. Validate
   → Run Omniverse Asset Validator to surface duplicate materials,
     hidden meshes, degenerate geometry, normals issues.

2. Optimize Materials
   → Deduplicates the redundant materials CAD exports tend to create.

3. Hidden Mesh Removal
   → Removes internal geometry invisible from the outside (sealed assets).

4. Decimate Meshes
   → Reduces tessellation density from manufacturing precision to
     rendering needs. Quality trade-off — review visually.

5. Merge Meshes (only if not instanced or geo-streamed)
   → Reduces draw-call/prim count for static content. Skip if your
     stage already uses scenegraph or point instancing, or if you are
     using geometry streaming.
```

The [Scene Optimizer How-To](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/howto.html) page has more on choosing operations.

## Industrial / VFI common findings

| Finding | Diagnostic | Operation |
|---------|------------|-----------|
| One huge mesh spanning the scene | Large bounding box in Statistics | Split and Merge (spatial clustering) |
| Thousands of identical fasteners | High prim count, low unique geometry | Point instancing or merge into parents |
| Every part has a unique material | Material count ≫ unique appearances | Optimize Materials |
| Internal hidden geometry | High triangle count vs visible surfaces | Hidden Mesh Removal |
| Excessive curve geometry | Slow rendering | Minimize widths or replace with meshes |
| Unnecessary UV coordinates | Extra memory and processing | Only add UVs for textured materials |

Reference: [VFI Performance Considerations](https://docs.omniverse.nvidia.com/vfi/latest/guide/performance-considerations.html).

## Material optimization pipeline

```
1. Import   → Produce clean USD with proper material mapping
2. Pre-Opt  → Scene Optimizer → Optimize Materials (USD-level dedup)
3. Runtime  → /app/usdrt/population/utils/mergeMaterials (Fabric-level dedup, see Platform Systems)
4. Render   → Material distilling (automatic in RTX Real-Time 2.0)
5. Export   → Bake to UsdPreviewSurface for cross-platform portability
```

Reference: [Materials Workflows](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/materials_workflows.html), [SimReady Material Best Practices](https://docs.omniverse.nvidia.com/simready/latest/simready-asset-creation/material-best-practices.html).

## Physics performance

| Technique | Impact | Configuration |
|-----------|--------|---------------|
| Primitive colliders | Fastest physics | Replace mesh colliders with spheres/boxes |
| GPU dynamics | Offload to GPU | `SimulationManager.set_physics_sim_device("cuda")` |
| Disable self-collisions | Reduce compute | Per-body physics setting |
| Adjust step size | Trade accuracy for speed | Larger step = faster |
| Minimum frame rate | Maintain FPS floor | `--/persistent/simulation/minFrameRate=<value>` |

**Collider ranking (fastest → slowest):** primitives (sphere, box, capsule) → convex → cylinders → complex triangle mesh. *Cylinders are sometimes intuitively grouped with primitives, but in the physics path they cost more than other primitive shapes — keep them separate in your mental model.* See [Isaac Sim Performance Optimization Handbook](https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/sim_performance_optimization_handbook.html) for the underlying detail.

## Reference / worked examples

- [AIF Pipeline Samples](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples) — worked examples of validation and conditioning pipelines for AIF.
- [VFI Samples (GitHub)](https://github.com/NVIDIA-Omniverse/vfi-samples) — VFI-specific content samples.
- [CAD to USD Workflows (Blog)](https://developer.nvidia.com/blog/building-cad-to-usd-workflows-with-nvidia-omniverse/).
