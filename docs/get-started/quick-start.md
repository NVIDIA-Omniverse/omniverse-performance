---
description: "Five-minute settings checklist, launch flags, and first-look workflow for a new scene"
---

# Quick Start

Most performance problems we see in customer escalations trace back to a small set of conditions that should have been verified before any serious work began. This is the five-minute checklist before reaching for the profiler.

## Quick reference — Do's and Don'ts

:::{admonition} DO: Reproduce against the latest Kit and a stock app template first
:class: tip

A surprising fraction of "performance issues" disappear once a partner moves from an older Kit branch to the current release on the unmodified Kit App Editor template. If the issue does not reproduce on the stock template, the problem is in the customizations on top of Kit, not Kit itself. Kit App Template repo: [kit-app-template](https://github.com/NVIDIA-Omniverse/kit-app-template).
:::

:::{admonition} DO: Verify these settings before starting a new project
:class: tip

| Setting | Path | Expected | Why |
|---------|------|----------|-----|
| Fabric Scene Delegate | `/app/useFabricSceneDelegate` | `true` (default Kit 109+) | FSD is the modern rendering pipeline. Older branches may have it explicitly disabled. ([FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)) |
| Frame timing display | Viewport overlay | Enabled, "No Pacing" | You can't optimize what you can't measure. |
| UJITSO derived-data cache | `/UJITSO/enabled` | `true` (default) | Caches derived textures, shaders, and (experimentally) geometry across sessions. ([UJITSO docs](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html)) |
:::

:::{admonition} DO: Apply these quick wins to any scene
:class: tip

- Use binary `.usdc` for all geometry and shading files; reserve `.usda` for small interface or debug files.
- Mark *referenced or payloaded* repeated assets as `instanceable=true`. (See {doc}`/reference/usd-scene-structure` for why this only helps when there are multiple references/payloads to the same asset.)
- Use payloads for heavy geometry and shading on model-style assets so consumers can open the stage unloaded.
- Run Scene Optimizer where applicable for your content type — see {doc}`/workflows/scene-optimization` for the bottleneck-driven decision guide.
- Keep the profiler or system monitoring visible while iterating.
:::

:::{admonition} DO: Apply these field-tested defaults on Linux benchmark and simulation hosts
:class: tip

These are operational defaults that recover real frame time on Linux hosts running Kit-based applications (Isaac Sim, Isaac Lab, headless Kit apps). Each is anchored to a measured fix in [Omniperf's `perf-tuning` skill](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md):

- **Set the Linux CPU governor to `performance`** before running benchmarks or production simulation. Leaving it on `powersave` or `schedutil` has been observed to cost on the order of milliseconds per frame in the field. Check with `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`; if it's not `performance`, switch with `sudo cpupower frequency-set -g performance` (or `echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`).
- **For simulation-only / RL / SDG / automated benchmark workloads, run headless** with `--no-window --/app/window/hideUi=True`, and disable viewport updates from Python (`get_active_viewport().updates_enabled = False`). Field measurements attribute several milliseconds per frame to viewport and UI work that is not needed for these workloads.
- **Avoid VNC / remote-desktop / virtual-display sessions** for benchmark or production runs. Virtual framebuffers can cause `PresentFrame` to dominate frame time. Use a physical monitor or run headless.
:::

:::{admonition} DON'T: Skip profiling because the smaller test scene works
:class: warning

Performance problems surface at scale.
:::

:::{admonition} DON'T: Assume default Kit settings are still optimal in a branched app
:class: warning

If your app branched off an older Kit App Template, your defaults may be out of date. Check the current Kit App Template repo when in doubt.
:::

:::{admonition} DON'T: Use `.usda` for large data files
:class: warning

`.usda` cannot be memory-mapped; it must be fully parsed on load. Use `.usdc`.
:::

:::{admonition} DON'T: Ship USDZ for runtime where load performance matters
:class: warning

USDZ front-loads all materials and textures and bypasses runtime caches. It's a fine packaged-delivery format, not a working file format.
:::

:::{admonition} DON'T: Trust the viewport HUD FPS when DLSS Frame Generation (DLSS-G) is on
:class: warning

DLSS-G inserts AI sub-frames between real frames, so the viewport HUD reports an inflated rate (commonly multiples of the real rendering rate, depending on the GPU generation). For benchmarking, comparison, or any decision based on a number, use Tracy frametime or another captured-trace measurement, not the HUD. DLSS-G should be disabled for simulation and benchmark runs ([Omniperf perf-tuning — DLSS-G](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/perf-tuning/SKILL.md#dlss-g-frame-generation--know-what-youre-measuring)).
:::

## Essential launch flags for large instanced scenes

```bash
# Enable FSD master switch
--/app/useFabricSceneDelegate=1

# Deduplicate Fabric-side material representations.
# Off by default since Kit 108 (opt-in) — incompatible with NeurayLib materials
# and material-swapping content. If your stage is static and uses neither, you
# generally want this on.
--/app/usdrt/population/utils/mergeMaterials=1

# Move scene-graph instancing work into the renderer.
# EXPERIMENTAL — RTX-only. Worth testing on heavily-instanced stages.
--/app/usdrt/population/utils/enableRendererInstancing=1
```

If you are touching any FSD setting beyond the defaults in your `.kit` file or launch flags, **add a comment explaining why**. Settings that exist to work around a specific bug or feature gap should be removable later — that's hard if no one remembers why they were set.

The deprecated `instanceCompactTransforms` setting is *not* part of this block. See {doc}`/reference/platform-systems` for the full FSD configuration reference.

## Your first five minutes with a new scene

1. **Open with the profiler available.** Press F8 to bring up the built-in profiler if `omni.kit.profiler.window` is loaded.
2. **Check the frame timing overlay.** Confirm renderer mode and frame time are visible.
3. **Sanity-check system resources.** Task Manager (Windows) or `nvidia-smi` (Linux) for CPU and GPU utilization. Use these as a hint, not a verdict — a profiler trace is the source of truth (see {doc}`profiling`).
4. **Identify the bottleneck class.** GPU-bound, CPU-bound, or memory-bound — go to {doc}`profiling` for the decision tree.
5. **Note your Kit version.** Many issues are already fixed in newer Kit releases. If you're on 107 or earlier, plan to test against 109/110.

:::{seealso}
- {doc}`profiling` — find the bottleneck before tuning
- {doc}`/about/kit-version-targeting` — why this guide assumes Kit 109/110
:::
