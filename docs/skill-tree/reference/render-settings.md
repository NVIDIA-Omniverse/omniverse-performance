---
description: "RTX render settings reference for the AI skill tree — bounces, DLSS, glass, multi-GPU"
---

# RTX Render Settings Reference

Source: [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html), [RTX Real-Time 2.0](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_rt.html), [Multi-GPU](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html).

## Key settings matrix

| Category | Setting | Recommended | Impact |
|----------|---------|-------------|--------|
| Bounces | Max Reflection | ≥2 (configurators), minimize for navigation | Direct FPS |
| Bounces | Max Refraction | 1 (thin-walled glass), 3+ (thick), 5+ (double-pane) | Significant when glass is present |
| Sampling | Samples per Pixel | 8 is a common baseline | Trade-off with noise |
| Sampling | Sampled Direct Lighting | Enable | Better lighting |
| Sampling | Roughness Sampling | Enable | Better specular |
| Thresholds | Invisible Light Reflections Roughness | ~0.01 | Culls rays that won't contribute |
| Thresholds | Invisible Light Refractions Roughness | ~0.01 | Same |
| Post | Tone Mapping (Iray) | Enable | Better color response |

## DLSS

| Technology | Modes | Use |
|------------|-------|-----|
| Super Resolution | Performance / Balanced / Quality / Auto | Always enable for interactive workflows |
| Frame Generation | On / Off | When apparent smoothness matters more than latency |

DLSS Ray Reconstruction is enabled automatically in RT 2.0 and Path Tracing — not a developer-controllable knob.

## Glass performance

| Type | Config | Min bounces | Cost |
|------|--------|-------------|------|
| Thin-walled (windows, walls) | `thin_walled=true` in OmniGlass | 1 | Lowest |
| Thick (bottles, solids) | Default OmniGlass | 3 | Higher |
| Double-pane | Two surfaces | 5 | Highest |

Architectural and automotive glass that is visually thin should be `thin_walled`. Everything else adds bounces. See [OmniGlass](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/templates/OmniGlass.html).

## Renderer comparison

| Feature | RT 2.0 | Interactive (Path Tracing) |
|---------|--------|-----------------------------|
| Speed | Faster | Slower |
| Material | Distilling (auto) | Full MDL |
| Use case | Navigation, twins, configurators | Final-quality images, marketing renders |

Material distilling is handled automatically by the renderer; not a setting partners need to tune.

## Multi-GPU

| Config | Default | Notes |
|--------|---------|-------|
| Identical GPUs | Enabled | Per [Multi-GPU docs](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_mgpu.html) |
| Mixed-model GPUs | Disabled | `/renderer/multiGpu/enabled` overrides; lowest-memory GPU caps the others |

Multi-GPU primarily helps when scaling viewport resolution or running many viewports/sensors. Before considering Multi-GPU, confirm you are not CPU-bound — that is the most common cause of disappointing scaling. We do not publish per-GPU speedup numbers because the published documentation does not commit to one and actual scaling is heavily resolution- and mode-dependent.
