---
name: perf-triage
description: Entry point for any Omniverse Kit or OpenUSD performance question. Triggers on "my scene is slow", "low FPS", "scene takes forever to load", "GPU crash", "out of memory", "performance problem", "how do I speed up", "optimize my scene". Classifies the problem and routes to the matching specialist skill.
domains:
  - omniverse
  - performance
owner: customer-success
tags:
  - omniverse
  - kit
  - usd
  - performance
  - triage
version: 1.0.0
---

# Performance Triage

Use this skill as the entry point for any "my Kit/OV/USD app is slow" question. It does three things:

1. Apply the three first-step checks before any deep diagnosis.
2. Classify the symptom into a known bucket.
3. Route to the specialist skill that owns the bucket.

## Step 1 — first-step checks (always do these first)

These three checks resolve a surprising fraction of "performance issues" outright. Apply them before any deeper diagnosis.

1. **Reproduce against the latest Kit.** Defaults assume Kit 109 / 110. Kit 107 is end-of-life or near it. Many issues are already fixed upstream.
2. **Reproduce against a stock Kit App Editor template** with custom extensions disabled. If the issue does not reproduce, the problem is in the user's customizations, not Kit. Repo: <https://github.com/NVIDIA-Omniverse/kit-app-template>.
3. **Check the GPU driver** against [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html). Wrong/unsupported drivers are one of the most common single root causes for crashes and surprising perf issues.

## Step 2 — classify the symptom

Match the user's description to one of these buckets:

| Symptom | Bucket | Next skill |
|---------|--------|-----------|
| Stage takes a long time to open | Loading | `profiling-guide` (activity timeline), then `usd-scene-structure` and `ujitso-manager` |
| Low FPS during navigation | Frame time | `profiling-guide`, then either `rendering-tuner` (GPU-bound) or `usdrt-advisor` (CPU-bound) |
| Excessive memory usage / OOM | Memory | `memory-optimizer`, then `fsd-configurator` if instanced |
| GPU crash / "device-lost" | Stability | `troubleshooting-router` |
| Performance regression after Kit upgrade | Regression | `troubleshooting-router` (Scenario 6) |
| "How do I structure my USD" / authoring questions | Authoring | `usd-scene-structure` |
| "How do I import CAD" / content pipeline | Content prep | `content-prep-advisor` |
| Cloud / container / cold-start | Deployment | `cloud-perf-advisor` |
| Work is **headless / standalone OpenUSD** — fix the file, no running Kit app needed | Authoring / optimization | Hand off to the [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) for an agent-driven optimization pass (see `AGENTS.md` → "When to hand off to the USD Performance Tuning skill") |
| Workload is **Isaac Sim** or **Isaac Lab** specifically | Robotics / RL | Hand off to [Omniperf](https://github.com/NVIDIA/omniperf) — start with [`diagnose-perf`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/diagnose-perf/SKILL.md), then chain into Omniperf's `profiling` and `nsys-analyze` |
| Need to **install** Nsight Systems / Tracy / capture tools | Tooling | [Omniperf `install-profilers`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/install-profilers/SKILL.md) |
| Need a **measured** FPS / GPU-util / startup number for comparison | Reference data | [Omniperf benchmark dashboards](https://nvidia.github.io/omniperf/) |

## Step 3 — what to do if the question is mixed

A typical mixed question (e.g., "my facility scene is at 5 FPS, has 300k instances, and 2000 materials") chains skills:

```
perf-triage
  → profiling-guide (confirm GPU- or CPU-bound)
  → usd-scene-structure (verify instanceable=true is on referenced/payloaded prims)
  → fsd-configurator (mergeMaterials, enableRendererInstancing — caveats apply)
  → rendering-tuner (DLSS, bounce counts on glass)
  → scene-optimizer-guide (only if the above don't resolve)
```

Always do triage first. Don't jump to Scene Optimizer or settings tuning before profiling.

## Defaults to recommend

- ✅ Run the latest Kit.
- ✅ Use binary `.usdc` files; reserve `.usda` for small interface/debug files.
- ✅ Keep `omni.kit.profiler.window` and `omni.kit.profiler.tracy` extensions loaded so F8 and Tracy actually work.
- ❌ Don't tune render settings before knowing it's a rendering problem.
- ❌ Don't add GPUs to fix a CPU bottleneck.

## Things to never recommend without qualification

- Specific FPS targets, prim-count thresholds, % improvements, or multi-GPU scaling factors. None of those are citable.
- The deprecated setting `/app/usdrt/population/utils/instanceCompactTransforms` (deprecated since Kit 108).

## Source guide section

[`docs/get-started/quick-start.md`](../../docs/get-started/quick-start.md), [`docs/get-started/profiling.md`](../../docs/get-started/profiling.md), [`docs/workflows/troubleshooting.md`](../../docs/workflows/troubleshooting.md).
