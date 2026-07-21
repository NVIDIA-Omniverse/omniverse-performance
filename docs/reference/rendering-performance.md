---
description: "Rendering performance reference: RTX modes, DLSS, glass, render settings, multi-GPU"
---

# Rendering Performance

Rendering settings have the most direct impact on interactive FPS. Picking the right render mode and keeping glass, bounces, and DLSS configured sensibly is usually enough to reach target frame rates on supported hardware — before any scene changes.

:::{seealso} Related agentic resource
To prove a render change actually moved frame time, capture a measured before/after with [OmniPerf](https://github.com/NVIDIA/omniperf). See {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Enable DLSS Super Resolution
:class: tip

It is effectively a free quality boost and should be on for any interactive workflow ([RTX Best Practices for Configurators](https://docs.omniverse.nvidia.com/guide_rtx-best-practices/latest/project-settings.html)).
:::

:::{admonition} DO: Use thin-walled mode for architectural glass
:class: tip

Windows, walls, and other single-surface glass only need one refraction bounce. Thick glass needs more, double-pane needs more still. OmniGlass has a `thin_walled` parameter for this ([OmniGlass](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/templates/OmniGlass.html)).
:::

:::{admonition} DO: Keep refraction and reflection bounce counts as low as the scene allows
:class: tip

Bounce count has a direct, measurable impact on GPU frame time. For real-time navigation, minimize; for static configurator frames, higher counts are affordable.
:::

:::{admonition} DO: Pick the right RTX mode for the task
:class: tip

RTX Real-Time 2.0 is the faster mode and is appropriate for navigation, digital twins, and most configurator workflows. RTX Interactive (Path Tracing) is for final-quality images and marketing renders, not interactive navigation ([RTX Real-Time 2.0](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_rt.html), [RTX Path Tracing](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_pt.html)).
:::

:::{admonition} DON'T: Default to Path Tracing for navigation
:class: warning

It's slower because it does more work; use it only when you need the image quality.
:::

:::{admonition} DON'T: Assume glass is correctly configured
:class: warning

Misconfigured glass is one of the most common avoidable GPU costs in industrial and automotive scenes. Check each glass material before optimizing other things.
:::

:::{admonition} DON'T: Mix GPU models when running multi-GPU
:class: warning

Per [RTX Multi-GPU](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html), Multi-GPU is disabled by default for mixed-GPU configurations. You can override this, but the GPU with the lowest memory will cap what the others can use.
:::

## Renderer mode selection

| | RTX Real-Time 2.0 | RTX Interactive (Path Tracing) |
|--|-------------------|--------------------------------|
| Use case | Navigation, digital twins, configurators | Final-quality images, marketing renders |
| Relative cost | Lower | Higher |
| DLSS | Supported | Supported |
| Multi-GPU | Supported | Supported — benefit is largest here |

Both modes are documented in the [RTX Renderer overview](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer.html). Per the [Multi-GPU docs](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html), Multi-GPU "lowers the cost of rendering more pixels and is ideal for high-resolution rendering, particularly for the RTX Interactive (Path Tracing) mode."

## DLSS

| Technology | What it does | When to use |
|------------|--------------|-------------|
| DLSS Super Resolution | AI upscaling from lower native resolution | Always — effectively free quality |
| DLSS Frame Generation | Generates intermediate AI sub-frames | When apparent smoothness matters more than latency — viewport display only |

Setting paths for these live in the [RTX Real-Time 2.0 docs](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_rt.html).

:::{admonition} DLSS Frame Generation inflates the viewport HUD FPS
:class: caution

DLSS-G inserts AI sub-frames between real frames. The viewport HUD reports the post–frame-generation rate, which is a multiple of the actual rendering rate (the multiplier depends on the GPU generation). For benchmarking, comparison, or any decision based on a number, use Tracy frametime — the captured-trace number is the authoritative one.

DLSS-G should be **disabled for simulation, RL, SDG, and automated benchmark runs**:

```bash
--/rtx-transient/dlssg/enabled=false  # default is off, but verify
```

Reference: [Omniperf perf-tuning — DLSS-G](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#dlss-g-frame-generation--know-what-youre-measuring).
:::

## Render settings that matter for FPS

The single biggest lever is bounce count. The others are worth understanding but have smaller impact for most scenes.

| Category | Setting | Recommended | Why |
|----------|---------|-------------|-----|
| Bounces | Max Reflection Bounces | ≥2 for static configurators; minimize for navigation | Direct FPS cost |
| Bounces | Max Refraction Bounces | 1 (thin-walled glass), 3+ (thick), 5+ (double-pane) | Dominates cost when glass is present |
| Sampling | Samples per Pixel | 8 is a common baseline | Trade-off with noise |
| Thresholds | Invisible Light Reflections Roughness | Near-zero (e.g. 0.01) | Culls rays that won't contribute |

Paths and UI locations live in [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html); these change occasionally between Kit versions, so check that page before hard-coding a setting path.

## Glass material performance

Glass is the single most common performance pitfall on industrial and automotive stages. If you have hundreds of window panes or car windshields, each extra refraction bounce compounds.

| Glass type | Configuration | Minimum bounces | Relative cost |
|------------|---------------|-----------------|---------------|
| Thin-walled (windows, walls) | `thin_walled=true` in [OmniGlass](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/templates/OmniGlass.html) | 1 | Lowest |
| Thick (bottles, solids) | Default OmniGlass | 3 | Higher |
| Double-pane | Two surfaces | 5 | Highest |

**Rule of thumb.** Architectural and automotive glass that is visually thin should be `thin_walled`. Everything else adds bounces.

## Material distilling — context only, not a setting

Material distilling converts complex MDL BSDFs into a simplified real-time representation in RTX Real-Time 2.0. It is handled by the renderer automatically and is not a user-exposed knob. The [MDL Distill and Bake extension](https://docs.omniverse.nvidia.com/extensions/latest/ext_material/ext_mdl-distill-and-bake.html) is a separate authoring-time tool for baking MDL to `UsdPreviewSurface` if you need cross-platform portability.

If distilling matters for your workflow, it's because you're authoring MDL and want the baked output to target a specific runtime — see the linked extension docs.

## Multi-GPU

Before considering multi-GPU at all, **make sure you are not CPU-bound** ({doc}`/get-started/profiling`). Throwing more GPUs at a CPU bottleneck will not improve frame rate — and that mistake is one we see repeatedly with partners scaling their hardware. Multi-GPU also adds CPU overhead for job distribution, per-GPU setup, and result gathering, which can make a CPU-bound workload *slower* once a second GPU is added ([Omniperf perf-tuning — Multi-GPU](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#multi-gpu--not-always-faster)).

Multi-GPU primarily helps when:

- You are scaling up viewport resolution.
- You are running many viewports or sensors (for example, Isaac workflows that simulate many cameras).
- You are in RTX Interactive (Path Tracing) mode where the per-pixel cost is higher.

Per the official [Multi-GPU documentation](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html):

- Multi-GPU is **on by default** when the system has multiple NVIDIA RTX-enabled GPUs of the same model.
- Benefits are largest at **high output resolutions** and in **RTX Interactive (Path Tracing)** mode. At low resolutions the renderer may fall back to single-GPU automatically.
- **Mixed GPU configurations are disabled by default** (`/renderer/multiGpu/enabled`). You can force them on, but the lowest-memory GPU caps what the others can use.
- Per-GPU VRAM is still the limit; Multi-GPU does not pool memory across cards.
- Multi-GPU helps rendering. It does **not** speed up physics, animation, or simulation work.

We deliberately do not publish a per-GPU speedup number here because the published documentation does not commit to one and the actual scaling depends heavily on resolution, mode, and scene. To measure scaling on a specific scene and hardware, use the built-in profiler and compare single-GPU vs multi-GPU frame time on the same view.
