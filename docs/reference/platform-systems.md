---
description: "FSD, UJITSO, streaming, and the Omniverse cache landscape — platform configuration reference"
---

# Platform Systems: FSD, UJITSO, Streaming & Caching

The Fabric Scene Delegate (FSD) and the UJITSO derived-data cache are the two platform systems most responsible for load-time and runtime performance on Kit applications. Most of what this section covers is configuration on setting paths under `/app/usdrt/` and `/UJITSO/`.

**Default-first.** The right starting point with FSD configuration is to run the defaults. Only change a setting when you have a specific reason — and when you do, leave a comment in your `.kit` file explaining *why*, so a future reader (or you) can revisit when the underlying issue is fixed in a later Kit release.

Defaults change between Kit versions. Where a default has moved, we list both values so you can tell whether your app matches the current defaults or an older branch.

:::{seealso} Related agentic resource
For installable skills and the broader performance toolset this guide points out to, see {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Verify FSD is enabled
:class: tip

`/app/useFabricSceneDelegate` defaults to `true` from Kit 109.0 onward; in earlier versions it defaulted to `false`. Older Kit App Template branches may have it explicitly disabled by workarounds that no longer apply. ([FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)).
:::

:::{admonition} DO: Enable `/app/usdrt/population/utils/mergeMaterials` for stages with many duplicate materials and no NeurayLib materials
:class: tip

`mergeMaterials` has been disabled by default since Kit 108 (it was `true` in earlier versions) — this is the stable default, not a temporary flip. It deduplicates identical materials to save memory, but it is incompatible with NeurayLib materials and affected variant/material-swapping content (notably automotive configurators), which is why it ships off. Treat it as an opt-in optimization: enable it for static stages with many duplicate materials that do not use NeurayLib materials or material swapping — such stages can load noticeably faster with it on. ([FSD Configuration — mergeMaterials](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html))
:::

:::{admonition} DO: Let UJITSO warm up
:class: tip

First load of a new scene is expected to be slower because UJITSO is populating the derived-data cache. Subsequent loads of the same assets use the cached derived data ([UJITSO Cache System](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html)).
:::

:::{admonition} DO: Leave texture streaming enabled for large scenes
:class: tip

The RTX renderer streams appropriate mip levels based on the view. Details and the VRAM budget setting live in [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html).
:::

:::{admonition} DO: Decide on `/app/usdrt/population/utils/populateAllAuthoredAttributes` based on what you need from Fabric
:class: tip

Default is `false` and that's the right default for rendering. Enable it only when you specifically need custom authored USD attributes accessible from Fabric — it costs memory, but for code paths that consume custom attributes, it's the supported way. ([FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html))
:::

:::{admonition} DON'T: Disable FSD unless you have a specific, documented reason
:class: warning

The OmniHydra fallback path is legacy.
:::

:::{admonition} DON'T: Ignore UJITSO "cache exceeded" warnings
:class: warning

Either increase the cache limit or clear old entries.
:::

:::{admonition} DON'T: Use `/app/usdrt/population/utils/instanceCompactTransforms`
:class: danger

This setting is **deprecated since Kit 108.0** and should no longer be used. The [FSD Configuration docs](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html) state: "Deprecated since version 108.0: This setting is deprecated from Kit 108.0 and should no longer be used." It is mutually exclusive with `useMatrixForInstanceProxyTransforms`, which is now the recommended path. Any older guide or template that recommended setting `instanceCompactTransforms=1` is stale — strip it from your `.kit` files.
:::

## Situational — worth testing, not defaults

These are not Do's or Don'ts. They are experimental flags that help on a specific kind of scene and need validation before shipping.

:::{admonition} Consider: `/app/usdrt/population/utils/enableRendererInstancing` for heavily instanced scenes
:class: caution

This flag moves scene-graph instancing work from Fabric population into the renderer, which can cut memory and improve frame time on large instanced stages. Officially marked **experimental** and supported only by the RTX renderer ([FSD Configuration — enableRendererInstancing](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)). Worth testing on the right kind of scene; validate before shipping. *Status as of Kit 109; re-check the docs for the current state.*
:::

:::{admonition} Consider: geometry streaming for scenes that exceed GPU memory
:class: caution

Geometry streaming dynamically loads/unloads geometry by view relevance. It is **disabled by default** and is considered experimental — it can unlock scenes that exceed GPU memory, but requires a restart after enabling, has fallbacks for some geometry types, and very high instance counts can still hurt TLAS update performance.
:::

## Fabric Scene Delegate (FSD)

### Data flow

```{mermaid}
flowchart LR
    stage["USD Stage"] --> pop["USDRT population<br/>(optimized, multi-threaded)"]
    pop --> fab["Fabric<br/>(rendering source of truth)"]
    fab --> fsd["Fabric Scene Delegate"]
    fsd --> hydra["Hydra"]
    hydra --> rtx["RTX Renderer"]
```

### Configuration reference

The [FSD Configuration page](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html) is the authoritative reference. We've intentionally narrowed this table to the settings partners commonly ask about — most other FSD-population flags should stay at their defaults.

| Setting | Path | Default | Recommendation | Status |
|---------|------|---------|----------------|--------|
| Enable FSD | `/app/useFabricSceneDelegate` | `true` (Kit 109+), `false` earlier | Always on | — |
| Merge materials | `/app/usdrt/population/utils/mergeMaterials` | `false` (Kit 108+), `true` earlier | Opt-in optimization — enable for static stages with many duplicate materials, not using NeurayLib materials | Off by default since Kit 108 (NeurayLib incompatibility) |
| Renderer-side instancing | `/app/usdrt/population/utils/enableRendererInstancing` | `false` | Test on heavily-instanced scenes | Experimental, RTX renderer only |
| Populate all authored attributes | `/app/usdrt/population/utils/populateAllAuthoredAttributes` | `false` | Off for rendering. Enable only when you specifically need custom attrs in Fabric — costs memory | — |
| Instance compact transforms | `/app/usdrt/population/utils/instanceCompactTransforms` | — | Do not use | Deprecated since Kit 108.0 |

A typical launch-flag block for a large instanced stage:

```bash
# FSD master switch
--/app/useFabricSceneDelegate=1

# Opt-in optimization: mergeMaterials is off by default (Kit 108+).
# Reason: static stage with many duplicate materials, no NeurayLib materials.
--/app/usdrt/population/utils/mergeMaterials=1

# EXPERIMENTAL: validate before shipping. RTX renderer only.
--/app/usdrt/population/utils/enableRendererInstancing=1
```

Touching any setting in your `.kit` file? Add a comment: feature, bug worked around, or expected future fix. That comment is what lets you remove the flag later when the issue is gone.

### Version-specific gotchas

- `useFabricSceneDelegate` default flipped to `true` in Kit 109.0.
- `mergeMaterials` has been off by default since Kit 108 — it's an opt-in optimization, off by default because it's incompatible with NeurayLib materials. Older guides recommending it default-on reflect pre-108 behavior.
- `instanceCompactTransforms` was deprecated in Kit 108.0. Older guides that recommend it are stale.

If you see a perf regression after a Kit upgrade, compare your `.kit` file against the current Kit App Template and check the FSD configuration page for defaults that changed.

## UJITSO (derived-data cache)

UJITSO caches derived data (mipmapped textures, compiled shaders, optimized geometry) so subsequent loads of the same assets can skip the processing step. The [UJITSO Derived Data Cache](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html) page is the canonical reference.

### Processors

| Processor | Input → Output | Default | Notes |
|-----------|----------------|---------|-------|
| Textures | Source images → GPU-ready formats + mipmaps | Enabled | Biggest first-load speedup |
| Materials | MDL source → compiled shader bytecode | Enabled | Avoids runtime compilation |
| Geometry | Raw mesh → optimized, merged, deduplicated | Experimental / off by default | Validate on your workload |

### Deployment models

| Model | Scope | Best for |
|-------|-------|----------|
| Local | Single user, single machine | Desktop workstations (default) |
| OmniHub | Multiple apps, same machine | Multi-app workflows |
| gRPC + DDCS | Multiple machines | Shared team caches, enterprise ([DDCS docs](https://docs.nvidia.com/nvcf/overview)) |

### Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| First load slow, subsequent fast | Normal cache miss on first load | None — expected |
| "Cache exceeded" warnings | Cache over its size limit | Increase the limit or clear old entries |
| Changed assets not reflecting | Stale cache | Set `/UJITSO/forceBuilds=true` or clear the cache directory |
| Need to debug cache behavior | — | Enable `/UJITSO/logBuildResults=true` |

Cache directories:

- Windows: `%LOCALAPPDATA%/ov/cache/DerivedDataCache`
- Linux: `~/.cache/ov/DerivedDataCache`

## Caching in Omniverse — what developers need to know

Omniverse has several independent caches, each serving a different layer (shaders, USD-derived data, USD content itself). For day-to-day desktop development you usually only touch UJITSO; for production deployments, especially cloud, you need to think about all of them.

| Cache | What it caches | Canonical docs |
|-------|----------------|----------------|
| UJITSO (derived data) | Mipmapped textures, compiled shaders, optimized geometry | [UJITSO](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html) |
| RTX shader cache (local) | Compiled RTX shaders | Local filesystem |
| GXCache (NVCF) | Shared compiled shaders across cloud function instances | [GXCache — NVIDIA Cloud Functions](https://docs.nvidia.com/nvcf/overview) |
| OKAS Memcached (Kit App Streaming) | Shared shader cache for streaming deployments | [Memcached service](https://docs.omniverse.nvidia.com/ovas/latest/deployments/infra/installation.html#install-memcached-service) |
| Omniverse Client Library | USD files and references, on local filesystem | [Omniverse Client Library](https://docs.omniverse.nvidia.com/kit/docs/client_library/latest/index.html) |
| USD Content Cache (UCC) | USD content for NVCF deployments | [UCC — NVIDIA Cloud Functions](https://docs.nvidia.com/nvcf/overview) |

A general overview of the cloud-deployment caches lives in [Simulation Cluster Caches — NVIDIA Cloud Functions](https://docs.nvidia.com/nvcf/overview). The caching picture is not the same across local, on-prem, and cloud deployments — see {doc}`/workflows/cloud-deployment` for deployment-specific guidance.

### Pre-warming

For a desktop workflow, running through a representative scene once is usually enough to warm UJITSO.

For a containerized / cloud deployment, cold starts pay every cache miss at once. A deliberate pre-warm step matters:

- **UJITSO:** load the target scene once during deployment warm-up so the derived data is cached before real user traffic hits.
- **Shader caches:** first render triggers shader compilation. For NVCF, use GXCache; for OKAS, use Memcached. Either needs to be populated by a pre-run render.
- **USD content:** the Omniverse Client Library caches USD files locally on first access. In cloud, use UCC or a CDN layer in front of your origin.

There is no single "warm up all caches" command — each cache is populated by its own triggering action (scene load, first render, first material evaluation).

## Streaming systems

| System | What it does | Default | When to enable |
|--------|--------------|---------|----------------|
| Texture streaming | Loads appropriate mip levels by view | Enabled | Always, for large scenes |
| Geometry streaming (experimental) | Loads geometry by view relevance | **Disabled** | Consider when the scene exceeds GPU memory; validate on your workload |
| Auto LOD | Generates cached LOD levels | With geometry streaming | Paired with geometry streaming |
| Instance streaming | Caps rendered instance count by relevance | With geometry streaming | Scenes with millions of instances |

Geometry streaming caveats (per the [GPU resources management docs](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html#gpu-resources-management)):

- Disabled by default; requires a restart after enabling.
- Some geometry types fall back to uncached processing.
- Auto-generated LODs trade fidelity for memory and streaming efficiency.
- Very high instance counts can still hurt TLAS update performance.

See [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html) for texture streaming configuration and the [VFI large-scene notes](https://docs.omniverse.nvidia.com/vfi/latest/guide/performance-considerations.html) for field experience with streaming on industrial scenes.
