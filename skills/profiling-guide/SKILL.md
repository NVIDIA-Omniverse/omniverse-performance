---
name: profiling-guide
description: Profiling Omniverse Kit applications — F8/Profiler Window, Tracy, the activity timeline for load-time analysis, Chrome Tracing, Nsight Systems, and the RTX performance heatmap. Triggers on "how to profile", "where is the bottleneck", "Tracy", "F8", "GPU usage", "instrument code", "performance traces", "activity timeline". Use this before tuning any settings.
domains:
  - omniverse
  - performance
owner: customer-success
tags:
  - omniverse
  - kit
  - profiling
  - tracy
  - performance
version: 1.0.0
---

# Profiling Guide

Always profile before tuning. Use this skill to pick the right tool and read the trace correctly.

## Required extensions

The profiling tools are not enabled in stripped-down Kit apps by default. Confirm these extensions are loaded before assuming a tool isn't available:

| Tool | Extension |
|------|-----------|
| Profiler Window (F8) | `omni.kit.profiler.window` |
| Tracy Profiler | `omni.kit.profiler.tracy` |

If an extension isn't loaded, the user's first action is to enable it — not to chase a different tool.

## Tool selection

| Tool | Best for | Notes |
|------|----------|-------|
| Profiler Window (F8) | First-look bottleneck identification | GPU/CPU frame times, nested zones |
| Tracy | Deep CPU analysis, long sessions, load-time | Live; correlate CPU and GPU with GPU profiling enabled |
| Chrome Tracing / Nsight Systems | Post-hoc analysis, sharing | From a captured trace |
| Activity timeline (built into Kit UI) | Load-time hotspots | Materials/textures dominating = caching or content-prep issue |
| Pixar USD profiler | Composition / population issues | USD/Hydra stack timings |
| Performance Heatmap (RTX Common Settings) | Per-pixel GPU cost | Find "expensive pixels" in the viewport |
| Task Manager / `nvidia-smi` | Sanity check | Hint, not diagnosis |

## Decision tree

The first branch is always *run the profiler*, not *check utilization*. CPU utilization is unreliable: a scene can be CPU-bound at 40% utilization if a single thread is saturated, or GPU-bound at 100% utilization if the CPU is spinning waiting on GPU.

```
Symptom?
├── Slow loading      → Tracy or activity timeline
│   └── Where is load time?
│       ├── Materials/textures dominate → ujitso-manager (cache cold)
│       ├── Composition dominates       → usd-scene-structure (layer/prim count)
│       └── Network/file fetch          → cloud-perf-advisor
├── Low FPS           → F8 or Tracy
│   └── Where is frame time?
│       ├── GPU       → rendering-tuner, scene-optimizer-guide
│       ├── CPU       → usdrt-advisor (Python traversal/TfNotice), usd-scene-structure (prim count)
│       └── OOM       → memory-optimizer
├── Memory growth    → memory-optimizer
└── GPU crash        → troubleshooting-router
```

## Do / Don't

- ✅ **DO** instrument your code from the start. Add profiling annotations so your functions appear in traces ([Instrumenting Code](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/profiling.html#instrumenting-code)). Without instrumentation, traces show engine frames but nothing about your logic.
- ✅ **DO** average across several seconds of representative workload — single-frame measurements are noisy.
- ✅ **DO** pay attention to outliers, not just averages. Constant hitching feels broken even when the average is fine; if every third frame is 5x the mean, the experience is degraded.
- ✅ **DO** test at production scale. A workflow that runs at 1k prims may break at 100k.
- ❌ **DON'T** rely on Task Manager / `nvidia-smi` utilization alone to classify the bottleneck.
- ❌ **DON'T** tune render settings before you know it's a rendering problem.

## Tracy quick configuration

- Enable GPU profiling in capture settings if you want CPU/GPU correlation.
- Enable CPU profiling for logic and animation.
- Sort zones by time to surface the most expensive operations first.
- Capture a few seconds of representative workload, not a single frame.

## Common CPU-side hotspots to look for

- Python stage traversal on large stages → recommend `usdrt-advisor` (USDRT fast stage queries).
- `TfNotice` callbacks firing on every change → recommend `usdrt-advisor` (USDRT change tracking, `UsdWatcher`).
- USD composition during runtime → load pre-composed stages.
- Physics stepping and animation evaluation.

## When to hand off to Omniperf

This skill answers *when and why* to profile and *how to read* a trace. For the operational side — capture commands, install steps, the COLD/WARM/TRACY methodology, run-to-run comparison — point the user at [Omniperf](https://github.com/NVIDIA/omniperf):

| If the user asks… | Hand off to |
|---|---|
| How do I install Nsight Systems / Tracy capture / csvexport / sqlite3? | [Omniperf `install-profilers`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/install-profilers/SKILL.md) |
| What's the canonical Tracy / `nsys` capture sequence on Kit? | [Omniperf `profiling`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/profiling/SKILL.md) |
| Carbonite profiler internals — backends, masks, channels, plot data | [Omniperf profiling guide](https://github.com/NVIDIA/omniperf/blob/main/dev/docs/profiling-guide.md) |
| How do I compare two `.nsys-rep` or `.tracy` runs? | [Omniperf `nsys-analyze`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/nsys-analyze/SKILL.md) |
| The user is on **Isaac Sim** or **Isaac Lab** specifically | [Omniperf `diagnose-perf`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/diagnose-perf/SKILL.md), then `profiling` and `nsys-analyze` |
| User wants a **measured** FPS / startup number to compare against | [Omniperf benchmark dashboards](https://nvidia.github.io/omniperf/) — this guide does not publish specific numbers |

## Source guide section

[`docs/get-started/profiling.md`](../../docs/get-started/profiling.md).
