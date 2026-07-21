---
description: "Common performance scenarios with step-by-step resolution and links back to the relevant reference chapter"
---

# Troubleshooting

Common patterns we see in field escalations on large industrial, automotive, and digital-twin stages. The intent of this section is *navigation*: each step links back to the chapter where the underlying technique is explained, rather than restating the technique here.

## Before you start: first three checks

Before any of the scenarios below, do these three things first — they resolve a surprising number of "performance issues" outright:

1. **Reproduce against the latest Kit.** Many issues are already fixed upstream. Kit 107 is approaching end-of-life; testing against Kit 109 or 110 should be the first step.
2. **Reproduce against a stock app template.** Disable custom extensions and run the workload in the Kit App Editor template. If it doesn't reproduce, the issue is in your app's customizations, not Kit.
3. **Check your GPU driver.** A wrong or unsupported driver is one of the most common root causes of crashes and surprising perf issues. See [Hardware & driver checks](#hardware-driver-checks) below.

## Scenario 1 — "My scene takes a long time to open"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | Check file format — convert `.usda` → `.usdc` for large files | {doc}`/reference/usd-scene-structure` |
| 2 | Audit layer count — keep it from exploding into the hundreds/thousands | {doc}`/reference/usd-scene-structure` |
| 3 | Implement payloads — lightweight interface → payload to heavy content | {doc}`/reference/usd-scene-structure` |
| 4 | Check UJITSO cache state — first load is expected to be slower | {doc}`/reference/platform-systems` |
| 5 | Check network and content cache | {doc}`cloud-deployment` |
| 6 | Use the activity timeline to see what dominates load | {doc}`/get-started/profiling` |
| 7 | Load without payloads or materials first, then enable incrementally | {doc}`/reference/usd-scene-structure` |

**Pro tip.** Combine steps 6 and 7: load with payloads off, watch the activity timeline, and progressively load to isolate the dominant cost.

## Scenario 2 — "FPS drops to single digits during navigation"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | Open the profiler (F8) — identify GPU-bound vs CPU-bound | {doc}`/get-started/profiling` |
| 2 | Check geometry bounds — extreme bounding boxes break RTX scene DB | {doc}`content-preparation` |
| 3 | Check instance count — very high counts may need streaming or point instancing | {doc}`/reference/usd-scene-structure` |
| 4 | Run Scene Optimizer with the operations matching your bottleneck | {doc}`scene-optimization` |
| 5 | Enable DLSS Super Resolution | {doc}`/reference/rendering-performance` |
| 6 | Reduce bounce counts (especially on glass) | {doc}`/reference/rendering-performance` |
| 7 | If GPU memory is the bottleneck, *consider* geometry streaming — experimental | {doc}`/reference/platform-systems` |

## Scenario 3 — "GPU crashes / device-lost errors"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | **Check your GPU driver version against the Technical Requirements** — the most common single root cause | [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html) |
| 2 | Clear UJITSO cache — stale or corrupt entries can cause crashes | {doc}`/reference/platform-systems` |
| 3 | Check texture streaming budget — may exceed VRAM | {doc}`/reference/platform-systems` |
| 4 | Reduce viewport count — each viewport consumes VRAM | {doc}`/reference/memory-and-resources` |
| 5 | Check for malformed USD — invalid subset indices, degenerate geometry | {doc}`content-preparation` |
| 6 | Update Kit SDK — stability fixes ship in newer versions | [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) |

## Scenario 4 — "Instanced scene still uses too much memory"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | Verify `instanceable=true` is set on the *referenced/payloaded* prim | {doc}`/reference/usd-scene-structure` |
| 2 | Verify the asset is actually referenced multiple times to the same source | {doc}`/reference/usd-scene-structure` |
| 3 | Enable `/app/usdrt/population/utils/enableRendererInstancing` (experimental) | {doc}`/reference/platform-systems` |
| 4 | Enable `/app/usdrt/population/utils/mergeMaterials` if many materials | {doc}`/reference/platform-systems` |
| 5 | Confirm Kit 109+ for zero-copy VtArray sharing — automatic | {doc}`/reference/memory-and-resources` |
| 6 | Consider point instancing for very high counts | {doc}`/reference/usd-scene-structure` |

## Scenario 5 — "Scene looks wrong after optimization"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | Run Generate Normals validator | {doc}`scene-optimization` |
| 2 | Check material assignments — dedup may have changed bindings | {doc}`scene-optimization` |
| 3 | Run Weld Checker for manifold issues | {doc}`scene-optimization` |
| 4 | Review Scene Optimizer report — identify which operation caused the issue | {doc}`scene-optimization` |
| 5 | Re-run with adjusted parameters (decimation tolerance, clustering size) | {doc}`scene-optimization` |

## Scenario 6 — "Performance regression after Kit upgrade"

| Step | Action | Where to look |
|------|--------|---------------|
| 1 | Read the Kit migration / release notes | [Kit 109.0 highlights](https://docs.omniverse.nvidia.com/dev-guide/latest/release-notes/109_0_highlights.html), [110.0 release notes](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer-release-notes/110_0.html) |
| 2 | Compare your `.kit` file against the current Kit App Template | [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) |
| 3 | Verify FSD is enabled — older workarounds may have disabled it | {doc}`/reference/platform-systems` |
| 4 | Check `mergeMaterials` — off by default since Kit 108; static stages with many duplicate materials (no NeurayLib materials) can enable it as an optimization | {doc}`/reference/platform-systems` |
| 5 | Check that no deprecated settings are still set (e.g. `instanceCompactTransforms`) | {doc}`/reference/platform-systems` |
| 6 | Test against the stock Kit App Template to isolate the divergence | [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) |

## Scenario 7 — "I have a Tracy or Nsight trace and want the named fix"

If you've already captured a profile and a recognizable zone is dominating frame time, this table maps common findings to a known operational fix. Each row cites the [Omniperf `perf-tuning` skill](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md), which is the source of truth for these field-tested settings on Kit-based applications. Verify the fix against your own scene with a [WARM benchmark run](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/profiling/SKILL.md#benchmark-accuracy-cold--warm--tracy) — profiling has overhead, so the authoritative FPS number always comes from a run with profiling off.

| Symptom in the trace | Likely cause | Fix | Reference |
|----------------------|--------------|-----|-----------|
| `PresentFrame` dominates frame time on a Linux host with VNC / virtual display | Virtual framebuffer present-timing issues | Use a physical monitor or run headless | [PresentFrame](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#presentframe-is-abnormally-slow) |
| `PresentFrame` dominates frame time but no VNC involved | GPU backpressure — GPU work exceeds frame budget | Reduce GPU workload (see {doc}`/reference/rendering-performance`); confirm GPU-bound first | [GPU backpressure](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#gpu-backpressure) |
| `resolveSamplerFeedback` zone is unexpectedly long, especially with multiple RenderProducts | Texture-streaming per-frame thread waits scaling with RenderProduct count | `--/rtx-transient/resourcemanager/enableTextureStreaming=false` — verify VRAM headroom first | [resolveSamplerFeedback](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#resolvesamplerfeedback-is-abnormally-slow) |
| Viewport / UI frames cost milliseconds in a simulation-only or RL run | Unnecessary viewport and UI work in headless workload | `--no-window --/app/window/hideUi=True`; from Python, `get_active_viewport().updates_enabled = False` | [Headless mode](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#headless-mode-34-ms-gpu-savings) |
| Viewport gizmo / manipulator overhead in dense scenes | Gizmos rendering in scenes with many objects | `--/persistent/app/viewport/gizmo/enabled=false` (and `displayOptions=0` for full hide) | [Viewport gizmos](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#viewport-gizmo-overhead) |
| Main-thread waits every frame even when the GPU is idle | `/app/hydraEngine/waitIdle=true` blocks every frame for GPU | `--/app/hydraEngine/waitIdle=false` for render-only workloads — keep `true` if you read GPU results same-frame (physics readback, synchronous sensors) | [HydraEngine waitIdle](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#hydraengine-waitidle) |
| Trace is missing PhysX detail (no `solver` / `fetchResults` / `integrate` zones) but physics is suspected | Default `--/app/profilerMask=1` filters out internal PhysX zones | Drop the mask (defaults to ALL) for the diagnostic capture | [PhysX tuning](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#physx-tuning) |
| Hot-reload / `fsWatcher` activity visible during a benchmark run | Extension change-detection running during benchmark | `--/app/extensions/fsWatcherEnabled=false` for benchmark runs only | [fsWatcher](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#extension-change-detection-fswatcher) |
| HUD viewport FPS is much higher than Tracy frametime suggests | DLSS Frame Generation is on; HUD includes AI sub-frames | Use Tracy frametime as the authoritative number; disable DLSS-G for benchmark / simulation: `--/rtx-transient/dlssg/enabled=false` | [DLSS-G](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#dlss-g-frame-generation--know-what-youre-measuring) |
| CPU frame time is high on a Linux host even after tuning | Linux CPU governor on `powersave` or `schedutil` | Set governor to `performance` (see {doc}`/get-started/quick-start`) | [CPU governor](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#cpu-governor) |
| Multi-GPU host doesn't show expected speedup | Multi-GPU only helps when clearly GPU-bound at high resolution / many cameras | Confirm GPU-bound first; otherwise adding GPUs adds CPU overhead with no benefit | [Multi-GPU](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#multi-gpu--not-always-faster) and {doc}`/reference/rendering-performance` |

For Isaac Sim / Isaac Lab–specific tuning (RTX presets, DLSS `execMode`, async PhysX, multi-camera render product verification), follow the link to the omniperf skill rather than restating the per-preset numbers here. Numbers are scene- and hardware-dependent; the omniperf skill keeps them version-stamped.

(hardware-driver-checks)=
## Hardware & driver checks

The single most common avoidable cause of crashes and unexpected performance is a wrong or unsupported GPU driver — partners are surprised by how often this is the answer.

| Check | What to look for |
|-------|------------------|
| GPU driver version | Match the supported range in [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html) |
| GPU model | Multi-GPU mixed configurations are off by default — see {doc}`/reference/rendering-performance` |
| GPU memory | Per-GPU VRAM is the limit; multi-GPU does not pool memory |
| OS | Match the supported OS list in Technical Requirements |
| CPU | Match the recommended core count for your workload |

When in doubt, link out to [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html) — it's the canonical, version-stamped source for hardware and driver guidance.

## When to escalate

If you've worked through the relevant scenarios and the problem persists:

1. Capture profiling data (Tracy trace or built-in profiler screenshots).
2. Document scene metrics (prim count, triangle count, material count, GPU/CPU utilization).
3. Note your Kit version, GPU model, GPU driver version, and OS.
4. Confirm the issue still reproduces against the latest Kit and the stock app template.
5. Share the above with NVIDIA support or your SA contact.
