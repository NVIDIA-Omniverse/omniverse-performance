---
description: "Find and diagnose GPU, CPU, memory, and load-time bottlenecks before tuning anything else"
---

# Profiling

Instrument your code from the beginning so that when a performance problem appears later, your own functions and scopes are already visible in profiler traces. Work top-down: confirm whether the issue is in load time, frame time (GPU or CPU), or memory before you start tuning settings.

:::{seealso} Related agentic resource
For the operational *how* — installing profilers, running canonical benchmarks, and capturing Tracy/Nsight traces — see [OmniPerf](https://github.com/NVIDIA/omniperf) and {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Instrument your code from the start
:class: tip

Add profiling annotations to your extensions so your functions appear in traces ([Instrumenting Code](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html#instrumenting-code)). Without instrumentation, traces show engine frames but nothing about your logic.
:::

:::{admonition} DO: Identify the bottleneck class before changing settings
:class: tip

The profiler extension ([Profiler Window](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler.html), requires `omni.kit.profiler.window`) attributes time to GPU work, CPU frames, and nested zones. Tracy ([Tracy Profiler Extension](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler_tracy.html), requires `omni.kit.profiler.tracy`) is the live deep-dive tool. The decision tree below assumes you have profiler data in front of you.
:::

:::{admonition} DO: Average across several seconds, not a single frame
:class: tip

Single-frame measurements are noisy. Capture a trace that spans several seconds of representative workload.
:::

:::{admonition} DO: Pay attention to outliers, not just averages
:class: tip

A scene with constant hitching feels broken even when its average frame time is fine. If every third frame takes five times the average, the experience is degraded — your eye sees the spikes, not the mean.
:::

:::{admonition} DO: Test at production scale
:class: tip

A workflow that runs fine at 1k prims may break at 100k. Profile on representative data.
:::

:::{admonition} DON'T: Rely on Task Manager / `nvidia-smi` utilization alone
:class: warning

High CPU utilization does not always mean CPU-bound, and low GPU utilization does not rule out a GPU bottleneck. OS-level utilization is a hint; a profiler trace is the source of truth.
:::

:::{admonition} DON'T: Tune render settings before you know it's a rendering problem
:class: warning

Changing DLSS, bounces, or materials when the real issue is Python stage traversal will waste time.
:::

:::{admonition} DON'T: Quote viewport HUD FPS as a benchmark number when DLSS Frame Generation is on
:class: warning

DLSS-G inserts AI sub-frames between real frames; the HUD reports an inflated rate. Use Tracy or another captured-trace frametime as the authoritative number, and disable DLSS-G for benchmark and simulation runs ([Omniperf perf-tuning — DLSS-G](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#dlss-g-frame-generation--know-what-youre-measuring)).
:::

:::{admonition} Profiler mask hides PhysX detail by default
:class: caution

The default `--/app/profilerMask=1` filters out internal PhysX zones, so a Tracy or Nsight capture taken with the default mask will not surface PhysX as a bottleneck even when it is one. Drop the mask to expose solver, `fetchResults`, and `integrate` zones when investigating physics-side stalls ([Omniperf perf-tuning — PhysX](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#physx-tuning)).
:::

## Profiling tools

Each row links to the docs for that tool, including the extension name you need to enable. Several of these tools are not enabled in stripped-down apps by default — confirm the extension is loaded before assuming the tool isn't available.

| Tool | Extension | What it shows | Best for | Typical overhead | Docs |
|------|-----------|---------------|----------|------------------|------|
| Built-in Profiler | `omni.kit.profiler.window` (F8) | GPU/CPU frame times, nested zones | First-look bottleneck identification | Low | [Profiler Window](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler.html) |
| Tracy Profiler | `omni.kit.profiler.tracy` | CPU core occupancy, thread deps, GPU context, live | Deep CPU analysis, long sessions, load-time analysis | ~5–15% | [Tracy](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler_tracy.html) |
| Chrome Tracing / Nsight Systems (NVTX) | Captured trace | Timeline of instrumented zones, accurate CUDA / Vulkan / GPU activity, HW counters | Post-hoc analysis, sharing with others, GPU work | ~10–20% | [Kit Profiling](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html#profiling) |
| Activity timeline | Built into Kit UI | High-level breakdown of what loaded when | Diagnosing load-time hotspots (caching, materials, textures) | Low | [Kit Profiling](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html) |
| Pixar USD profiler | USD profiler extension | USD/Hydra stack timings | Composition and population issues | Low | [Kit Profiling](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html) |
| Performance Heatmap | RTX Common settings | Per-pixel rendering cost | Finding "expensive pixels" in the viewport | Low | [Performance Heat Map Views](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html#performance-heat-map-views) |
| Task Manager / `nvidia-smi` | OS | Coarse utilization and memory | Sanity check, not diagnosis | None |  |

The Tracy and Nsight overhead figures are reference numbers measured on Kit-based applications and are documented in the [Omniperf profiling guide](https://github.com/NVIDIA/omniperf/blob/main/dev/docs/profiling-guide.md). They are not negligible: never quote benchmark FPS from a profiled run. Capture once with profiling off (the authoritative number), then again with the profiler enabled (for analysis only).

## Diagnosis decision tree

The first branch is always *run the profiler*, not *check utilization*. CPU utilization in particular is unreliable: a scene can be CPU-bound at 40% CPU utilization if a single thread is saturated, or GPU-bound at 100% CPU utilization if the CPU is spinning while waiting on GPU work. The profiler also helps with load-time issues — the activity timeline shows when materials or textures dominate load, which is usually a caching or content-prep issue.

```{mermaid}
flowchart TD
    s["Performance problem"] --> q1{"What is the symptom?"}
    q1 -->|"Slow scene loading"| loadprof["Open profiler / Tracy<br/>or activity timeline"]
    q1 -->|"Low FPS during navigation"| runprof["Open profiler F8<br/>or capture Tracy trace"]
    q1 -->|"Excessive memory usage"| mem["Memory issue"]
    q1 -->|"GPU crash / device-lost"| crash["Stability issue"]
    loadprof --> q3{"Where is load time spent?"}
    q3 -->|"Materials / textures dominate"| s7c["Caching cold<br/>or content not cached-friendly"]
    q3 -->|"Composition dominates"| s3a["USD structure<br/>layer/prim count"]
    q3 -->|"Network / file fetch dominates"| s10["Cloud / network<br/>caching"]
    runprof --> q2{"Where is frame time?"}
    q2 -->|"GPU frame time dominates"| gpu["GPU-bound"]
    q2 -->|"CPU frame time dominates"| cpu["CPU-bound"]
    q2 -->|"Allocations / OOM in trace"| membound["Memory-bound"]
    s7c --> s7["Platform Systems<br/>UJITSO"]
    s3a --> s3["USD Structure"]
    s10 --> sCloud["Cloud Deployment"]
    gpu --> s6["Rendering<br/>Scene Optimizer"]
    cpu --> s4["Prim count<br/>USDRT / Fabric"]
    membound --> s8["Memory<br/>Streaming"]
    mem --> s8
    crash --> s11["Troubleshooting"]
```

## GPU bottleneck workflow

1. Check whether the issue is camera-dependent. A slowdown that appears only in certain areas of the stage usually points to a localized GPU hotspot.
2. Enable the [Performance Heatmap View in RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html#performance-heat-map-views) to visualize per-pixel cost.
3. Typical causes of "expensive pixels":
   - Complex materials with many layers or translucency
   - Overlapping meshes or extreme bounding boxes
   - Glass materials with too many refraction bounces — see {doc}`/reference/rendering-performance`
4. Use the [Omni Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html) to identify geometry issues such as degenerate faces and bad normals.

## CPU bottleneck workflow

1. Confirm your own code is instrumented — otherwise your functions won't appear in the trace.
2. Capture a performance trace using the [Kit profiling guide](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html#profiling). Chrome Tracing and Nsight Systems are good for post-hoc analysis; Tracy is best for live inspection.
3. Common expensive CPU operations to look for in the trace:
   - Python stage traversal on large stages — prefer [USDRT fast stage queries](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/usdrt_query.html).
   - `TfNotice` callbacks firing on every stage change — prefer [USDRT change tracking](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/changetracking.html) or [`UsdWatcher`](https://docs.omniverse.nvidia.com/kit/docs/omni.usd/latest/omni.usd/omni.usd.UsdWatcher.html).
   - USD composition during runtime — prefer loading pre-composed stages.
   - Physics stepping and animation evaluation.

## Load-time workflow

Tracy is useful for load-time as well as runtime analysis. The activity timeline window inside Kit gives a high-level breakdown of where load time was spent — when materials and textures dominate that view, you usually have a UJITSO cache miss or texture-prep issue, not a scene-structure problem ({doc}`/reference/platform-systems`). Composition-heavy load time points instead at scene structure and layer count ({doc}`/reference/usd-scene-structure`).

## Tracy configuration

Tracy can be overwhelming by default. Useful practices:

- Enable GPU profiling in the capture settings if you want to correlate CPU and GPU timelines.
- Enable CPU profiling for logic and animation.
- Sort zones by time to surface the most expensive operations first.
- Capture a few seconds of a representative workload rather than a single frame.

## Establishing a baseline

1. Launch the application with **no scene loaded**.
2. Record idle metrics: CPU %, system RAM GB, GPU %, GPU VRAM GB.
3. Load your target scene and wait until FPS stabilizes.
4. Record loaded metrics. Scene overhead is *loaded − idle*.

:::{seealso} Operational depth — Omniperf
This page covers *when and why* to profile. For *how to actually capture, store, and compare traces* on Kit-based applications (Isaac Sim, Isaac Lab, Kit SDK), see the operational counterpart:

- [Omniperf `profiling` skill](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/profiling/SKILL.md) — canonical Tracy + Nsight Systems capture sequence, COLD/WARM/TRACY measurement separation, and last-resort force-kill handling.
- [Omniperf `nsys-analyze` skill](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/nsys-analyze/SKILL.md) — analyze captured `.nsys-rep` and `.tracy` files; compare two runs.
- [Omniperf profiling guide](https://github.com/NVIDIA/omniperf/blob/main/dev/docs/profiling-guide.md) — the source-of-truth reference for the Carbonite profiling subsystem (backends, masks, channels, plot data, event annotations).
- [Omniperf benchmark dashboards](https://nvidia.github.io/omniperf/) — measured Isaac Sim and Isaac Lab numbers by GPU and commit. This guide does not publish specific numbers; the dashboards are the citable reference.
:::
