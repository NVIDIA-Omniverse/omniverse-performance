---
name: rendering-tuner
description: RTX rendering performance — RT 2.0 vs Path Tracing, DLSS, glass, bounces, multi-GPU. Triggers on "render settings", "RTX", "DLSS", "RT 2.0 vs path tracing", "bounces", "samples per pixel", "refraction", "glass performance", "multi-GPU", "improve FPS", "scaling resolution".
domains:
  - omniverse
  - rendering
owner: customer-success
tags:
  - rtx
  - rendering
  - dlss
  - mdl
  - multi-gpu
  - performance
version: 1.0.0
---

# Rendering Performance Tuner

Rendering settings are the most direct lever on interactive FPS. Picking the right RTX mode and keeping glass, bounces, and DLSS configured sensibly is usually enough to reach target frame rates on supported hardware — before any scene changes.

## Renderer mode selection

| | RTX Real-Time 2.0 | RTX Interactive (Path Tracing) |
|--|-------------------|--------------------------------|
| Use case | Navigation, digital twins, configurators | Final-quality images, marketing renders |
| Relative cost | Lower | Higher |
| DLSS | Supported | Supported |
| Multi-GPU | Supported | Supported — benefit largest here |

## Do / Don't

- ✅ **DO** enable DLSS Super Resolution. Effectively a free quality boost; on for any interactive workflow.
- ✅ **DO** use thin-walled mode for architectural glass. `thin_walled=true` on OmniGlass for windows, walls, single-surface glass — they only need 1 refraction bounce.
- ✅ **DO** keep refraction and reflection bounce counts as low as the scene allows. Direct, measurable impact on GPU frame time.
- ✅ **DO** pick the right RTX mode for the task. RT 2.0 for navigation; Path Tracing only for final-quality.
- ❌ **DON'T** default to Path Tracing for navigation.
- ❌ **DON'T** assume glass is correctly configured. Misconfigured glass is the most common avoidable GPU cost on industrial/automotive stages.
- ❌ **DON'T** mix GPU models when running multi-GPU. Mixed-GPU is disabled by default; the lowest-memory GPU caps the others.

## DLSS

| Technology | What it does | When to use |
|------------|--------------|-------------|
| DLSS Super Resolution | AI upscaling from lower native resolution | Always — effectively free quality |
| DLSS Frame Generation | Generates intermediate frames | When apparent smoothness matters more than latency |

**DLSS Ray Reconstruction** is enabled automatically in RT 2.0 and Path Tracing — not a developer-controllable knob. **Do not list it as a tuning option.**

## Render settings that matter

| Category | Setting | Recommended | Why |
|----------|---------|-------------|-----|
| Bounces | Max Reflection Bounces | ≥2 for static configurators; minimize for navigation | Direct FPS cost |
| Bounces | Max Refraction Bounces | 1 (thin-walled glass), 3+ (thick), 5+ (double-pane) | Dominates cost when glass is present |
| Sampling | Samples per Pixel | 8 is a common baseline | Trade-off with noise |
| Thresholds | Invisible Light Reflections Roughness | Near-zero (e.g. 0.01) | Culls rays that won't contribute |

The biggest lever is bounce count. Setting paths live in [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html); they change occasionally between Kit versions.

## Glass material performance

| Glass type | Configuration | Min bounces | Cost |
|------------|---------------|-------------|------|
| Thin-walled (windows, walls) | `thin_walled=true` in OmniGlass | 1 | Lowest |
| Thick (bottles, solids) | Default OmniGlass | 3 | Higher |
| Double-pane | Two surfaces | 5 | Highest |

If a partner has hundreds of windows or car windshields, every extra refraction bounce compounds. Architectural and automotive glass that's visually thin should be `thin_walled`.

## Material distilling — context only

Material distilling converts complex MDL BSDFs into a simplified real-time representation in RT 2.0. **It is handled by the renderer automatically and is not a user-exposed knob.** The MDL Distill and Bake extension is a separate authoring-time tool for baking MDL to `UsdPreviewSurface` if cross-platform portability is needed.

Do not present material distilling as a setting users can toggle.

## Multi-GPU — read this before recommending

Before considering Multi-GPU at all, **make sure the user is not CPU-bound** (route to `profiling-guide`). Throwing more GPUs at a CPU bottleneck will not improve frame rate — and that mistake is one we see repeatedly.

Multi-GPU primarily helps when:

- Scaling up viewport resolution.
- Running many viewports or sensors (Isaac workflows simulating many cameras).
- In Path Tracing mode where per-pixel cost is higher.

Per the official docs:

- Multi-GPU is on by default with multiple identical NVIDIA RTX-enabled GPUs.
- Benefits largest at high resolutions and in Path Tracing mode. At low resolutions the renderer may fall back to single-GPU.
- Mixed-GPU disabled by default (`/renderer/multiGpu/enabled`); lowest-memory GPU caps the others.
- Per-GPU VRAM is the limit — Multi-GPU does not pool memory.
- Multi-GPU helps rendering. **It does not speed up physics, animation, or simulation work.**

**Do not publish a per-GPU speedup number.** The official documentation does not commit to one and actual scaling depends on resolution, mode, and scene.

## Source guide section

[`docs/reference/rendering-performance.md`](../../docs/reference/rendering-performance.md).

External references: [RTX Best Practices for Configurators](https://docs.omniverse.nvidia.com/guide_rtx-best-practices/latest/project-settings.html), [RTX Real-Time 2.0](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_rt.html), [Multi-GPU Rendering](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html), [OmniGlass](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/templates/OmniGlass.html).
