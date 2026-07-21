---
name: content-prep-advisor
description: Content preparation, validation, CAD import, materials pipeline, and physics — preventing performance issues at the source. Triggers on "import CAD", "CAD to USD", "validate USD", "asset validator", "usdchecker", "material pipeline", "primitive collider", "mesh collider", "physics performance", "PhysX", "DDS texture".
domains:
  - omniverse
  - content-pipeline
owner: customer-success
tags:
  - cad
  - usd
  - validation
  - materials
  - physics
  - simready
version: 1.0.0
---

# Content Preparation Advisor

The quality of input data determines the performance ceiling. CAD imports authored for manufacturing precision, with thousands of duplicate materials and hidden internal geometry, will be slow no matter how well rendering is tuned. Content conditioning is where the biggest leverage usually lives.

> **Headless USD work?** The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) operates on USD files directly. Hand off when the task is "fix the USD" rather than tune a running Kit app — see `AGENTS.md` → "When to hand off to the USD Performance Tuning skill."

## Validation tool selection

Pick the simplest tool that fits the task:

| Tool | Use for |
|------|---------|
| [`usdchecker`](https://openusd.org/release/api/md_pxr_usd_validation_usd_validation__r_e_a_d_m_e.html) | Baseline OpenUSD compliance ("is this USD structurally valid?") |
| [Omniverse Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html) | Richer rules, UI/CLI/Python, possible auto-fixes, CI/CD integration |
| [OpenUSD Validation framework](https://docs.nvidia.com/learn-openusd/latest/data-exchange/asset-validation/what-is-asset-validation.html) | Custom validators or suites for organization-specific policies |

Wire validation into CI/CD so regressions in exchanged USD output are caught at the importer/exporter boundary, not in production.

The Asset Validator also runs **standalone, without Kit**: `pip install usd-validation-nvidia` ([PyPI](https://pypi.org/project/usd-validation-nvidia/)) gives you the same engine as a pure-Python package with a CLI (`nvidia_usd_validate`) and Python API — which is what makes the CI/CD wiring above practical. Use `usd-validation-nvidia`; the older `omniverse-asset-validator` package is frozen.

## Do / Don't

- ✅ **DO** validate USD assets early and often.
- ✅ **DO** look at the geometry, run validators, then use Scene Optimizer where applicable. Don't run a full optimizer pipeline blindly. Validators tell you what's wrong; route to `scene-optimizer-guide` for the operations.
- ✅ **DO** use "Import as Reference" for aggregation workflows — modular, references the source.
- ✅ **DO** use primitive colliders instead of mesh colliders for physics. Spheres and boxes are orders of magnitude faster than complex triangle meshes.
- ✅ **DO** fix at the source pipeline when possible. If validation or Scene Optimizer keeps finding the same kinds of waste, the connector or upstream tool is the right place to fix it.
- ❌ **DON'T** import CAD data and use it as-is. CAD models are authored for manufacturing precision, not real-time rendering.
- ❌ **DON'T** add UV coordinates to meshes that don't need textures.
- ❌ **DON'T** use mesh colliders when simpler shapes will do.

## CAD import methods

| Method | When to use | Notes |
|--------|-------------|-------|
| CAD Converter | Batch / automated conversion | Plan a post-conversion validation and conditioning pass |
| Direct DCC export | Direct from authoring tool | Quality depends on the exporter |
| Import to Stage | Editing in current session | Embeds data — can bloat the stage |
| Import as Reference | Aggregation workflows | Modular, references the source file |

**Memory requirement.** 16 GB minimum for CAD conversion; complex files may need 32 GB.

## Post-import optimization — example workflow

This is *one* example workflow, not a prescription. **It does not apply to content that's already properly instanced or uses geometry streaming** — merging meshes in those cases is counter-productive.

```
1. Validate (Omniverse Asset Validator)
   → Surface duplicate materials, hidden meshes, degenerate geometry, normals issues.

2. Optimize Materials
   → Deduplicates the redundant materials CAD exports tend to create.

3. Hidden Mesh Removal
   → Removes internal geometry invisible from the outside (sealed assets).

4. Decimate Meshes
   → Reduces tessellation density. Quality trade-off — review visually.

5. Merge Meshes (only if not instanced or geo-streamed)
   → Reduces draw-call/prim count. Skip if scenegraph/point instancing is in use,
     or if geometry streaming is enabled.
```

## Industrial / VFI common findings

| Finding | Diagnostic | Operation |
|---------|-----------|-----------|
| One huge mesh spanning the scene | Large bounding box in Statistics | Split and Merge |
| Thousands of identical fasteners | High prim count, low unique geometry | Point instancing or merge into parents |
| Every part has a unique material | Material count ≫ unique appearances | Optimize Materials |
| Internal hidden geometry | High triangle count vs visible surfaces | Hidden Mesh Removal |
| Excessive curve geometry | Slow rendering | Minimize widths or replace with meshes |
| Unnecessary UV coordinates | Extra memory and processing | Only add UVs for textured materials |

## Material optimization pipeline

```
1. Import   → Produce clean USD with proper material mapping
2. Pre-Opt  → Scene Optimizer → Optimize Materials (USD-level dedup)
3. Runtime  → /app/usdrt/population/utils/mergeMaterials (Fabric-level dedup;
              see fsd-configurator for the mergeMaterials default context)
4. Render   → Material distilling (automatic in RTX Real-Time 2.0)
5. Export   → Bake to UsdPreviewSurface for cross-platform portability
```

## Physics performance

| Technique | Impact | Configuration |
|-----------|--------|---------------|
| Primitive colliders | Fastest physics | Replace mesh colliders with spheres/boxes |
| GPU dynamics | Offload to GPU | `SimulationManager.set_physics_sim_device("cuda")` |
| Disable self-collisions | Reduce compute | Per-body physics setting |
| Adjust step size | Trade accuracy for speed | Larger step = faster |
| Minimum frame rate | Maintain FPS floor | `--/persistent/simulation/minFrameRate=<value>` |

**Collider ranking (fastest → slowest):** primitives (sphere, box, capsule) → convex → cylinders → complex triangle mesh.

*Cylinders are sometimes intuitively grouped with primitives, but in the physics path they cost more than other primitive shapes — keep them separate in your mental model when explaining to users.*

## Worked examples

- [AIF Pipeline Samples](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples) — validation and conditioning pipelines for AIF.
- [VFI Samples (GitHub)](https://github.com/NVIDIA-Omniverse/vfi-samples) — VFI-specific content samples.

## Source guide section

[`docs/workflows/content-preparation.md`](../../docs/workflows/content-preparation.md).
