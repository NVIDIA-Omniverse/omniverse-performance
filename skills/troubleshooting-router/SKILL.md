---
name: troubleshooting-router
description: Common performance scenarios with step-by-step resolution and routing back to the relevant specialist skill. Triggers on "GPU crash", "device-lost", "scene takes 30 minutes to open", "performance regression after Kit upgrade", "FPS drops to single digits", "instanced scene uses too much memory", "scene looks wrong after optimization", "Kit upgrade broke performance".
domains:
  - omniverse
  - troubleshooting
owner: customer-success
tags:
  - troubleshooting
  - kit
  - performance
  - regression
version: 1.0.0
---

# Troubleshooting Router

Common patterns we see in field escalations. The intent of this skill is *navigation*: each step links back to the specialist skill that owns the technique.

## Before any scenario — first three checks

These resolve a surprising fraction of "performance issues" outright. Apply them before any deeper diagnosis:

1. **Reproduce against the latest Kit** (109 or 110). Many issues are already fixed upstream.
2. **Reproduce against a stock app template**. Disable custom extensions; run in the Kit App Editor template. If it doesn't reproduce, the issue is in customizations, not Kit.
3. **Check the GPU driver** against [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html). Wrong/unsupported drivers are the most common single root cause for crashes.

## Scenario 1 — "My scene takes a long time to open"

| Step | Action | Skill |
|------|--------|-------|
| 1 | Convert `.usda` → `.usdc` for large files | `usd-scene-structure` |
| 2 | Audit layer count — keep it from exploding into the hundreds/thousands | `usd-scene-structure` |
| 3 | Implement payloads — lightweight interface → payload to heavy content | `usd-scene-structure` |
| 4 | Check UJITSO cache state — first load is expected to be slower | `ujitso-manager` |
| 5 | Check network and content cache | `cloud-perf-advisor` |
| 6 | Use the activity timeline to see what dominates load | `profiling-guide` |
| 7 | Load without payloads or materials first, then enable incrementally | `usd-scene-structure` |

**Pro tip.** Combine steps 6 and 7: load with payloads off, watch the activity timeline, progressively load to isolate the dominant cost.

## Scenario 2 — "FPS drops to single digits during navigation"

| Step | Action | Skill |
|------|--------|-------|
| 1 | Open the profiler (F8) — identify GPU-bound vs CPU-bound | `profiling-guide` |
| 2 | Check geometry bounds — extreme bounding boxes break RTX scene DB | `content-prep-advisor` |
| 3 | Check instance count — very high counts may need streaming or point instancing | `usd-scene-structure` |
| 4 | Run Scene Optimizer with operations matching the bottleneck | `scene-optimizer-guide` |
| 5 | Enable DLSS Super Resolution | `rendering-tuner` |
| 6 | Reduce bounce counts (especially on glass) | `rendering-tuner` |
| 7 | If GPU memory is the bottleneck, *consider* geometry streaming — ⚠️ experimental | `fsd-configurator` |

## Scenario 3 — "GPU crashes / device-lost errors"

| Step | Action | Skill |
|------|--------|-------|
| 1 | **Check GPU driver against [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html)** — most common single root cause | (this skill) |
| 2 | Clear UJITSO cache — stale or corrupt entries can cause crashes | `ujitso-manager` |
| 3 | Check texture streaming budget — may exceed VRAM | `memory-optimizer` |
| 4 | Reduce viewport count | `memory-optimizer` |
| 5 | Check for malformed USD — invalid subset indices, degenerate geometry | `content-prep-advisor` |
| 6 | Update Kit SDK — stability fixes ship in newer versions | (this skill) |

## Scenario 4 — "Instanced scene still uses too much memory"

| Step | Action | Skill |
|------|--------|-------|
| 1 | Verify `instanceable=true` is on the *referenced/payloaded* prim | `usd-scene-structure` |
| 2 | Verify the asset is actually referenced multiple times to the same source | `usd-scene-structure` |
| 3 | Enable `/app/usdrt/population/utils/enableRendererInstancing` (⚠️ experimental) | `fsd-configurator` |
| 4 | Enable `/app/usdrt/population/utils/mergeMaterials` if many materials | `fsd-configurator` |
| 5 | Confirm Kit 109+ for zero-copy VtArray sharing — automatic | `memory-optimizer` |
| 6 | Consider point instancing for very high counts | `usd-scene-structure` |

## Scenario 5 — "Scene looks wrong after optimization"

| Step | Action | Skill |
|------|--------|-------|
| 1 | Run Generate Normals validator | `scene-optimizer-guide` |
| 2 | Check material assignments — dedup may have changed bindings | `scene-optimizer-guide` |
| 3 | Run Weld Checker for manifold issues | `scene-optimizer-guide` |
| 4 | Review Scene Optimizer report — identify which operation caused it | `scene-optimizer-guide` |
| 5 | Re-run with adjusted parameters | `scene-optimizer-guide` |

## Scenario 6 — "Performance regression after Kit upgrade"

| Step | Action | Skill |
|------|--------|-------|
| 1 | Read Kit migration / release notes | (this skill) |
| 2 | Compare `.kit` file against current Kit App Template | (this skill) |
| 3 | Verify FSD is enabled — older workarounds may have disabled it | `fsd-configurator` |
| 4 | Check `mergeMaterials` — off by default since Kit 108; static stages with many duplicate materials (no NeurayLib materials) can enable it as an optimization | `fsd-configurator` |
| 5 | Strip deprecated settings (e.g. `instanceCompactTransforms`) | `fsd-configurator` |
| 6 | Test against the stock Kit App Template to isolate the divergence | (this skill) |

## Hardware & driver checks (most common avoidable cause)

The single most common avoidable cause of crashes and unexpected performance is a wrong or unsupported GPU driver — partners are surprised by how often this is the answer.

| Check | What to look for |
|-------|------------------|
| GPU driver version | Match the supported range in [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html) |
| GPU model | Multi-GPU mixed configurations are off by default (route to `rendering-tuner`) |
| GPU memory | Per-GPU VRAM is the limit; multi-GPU does not pool memory |
| OS | Match the supported OS list in Technical Requirements |
| CPU | Match the recommended core count for the workload |

## When to escalate

If the user has worked through the relevant scenarios and the problem persists, ask them to capture:

1. Profiling data (Tracy trace or built-in profiler screenshots).
2. Scene metrics (prim count, triangle count, material count, GPU/CPU utilization).
3. Kit version, GPU model, GPU driver version, OS.
4. Confirmation that the issue still reproduces against the latest Kit and the stock app template.

Then route to NVIDIA support or their SA contact.

## Source guide section

[`docs/workflows/troubleshooting.md`](../../docs/workflows/troubleshooting.md).
