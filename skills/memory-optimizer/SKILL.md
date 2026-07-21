---
name: memory-optimizer
description: GPU and system memory, threading, async rendering, and texture sizing. Triggers on "GPU memory", "VRAM", "out of GPU memory", "RAM usage", "system memory", "memory leak", "thread count", "8K texture", "DDS", "texture compression", "viewport memory".
domains:
  - omniverse
  - kit
  - performance
owner: customer-success
tags:
  - memory
  - vram
  - kit
  - performance
  - textures
version: 1.0.0
---

# Memory Optimizer

GPU memory exhaustion is a common crash cause. System memory mismanagement leads to slow performance long before it crashes. CPU thread configuration can mean the difference between half and full target frame rate.

## GPU memory checklist (bullets, not priority)

Pick what matches the bottleneck. **Do not present this as a numbered priority order** — the right action depends on what the workload looks like.

- Enable texture streaming. Loads only the needed mip levels.
- Consider geometry streaming + auto LOD on scenes that exceed GPU memory. ⚠️ Experimental — restart required after enabling, fallback for some geometry types, very high instance counts can hurt TLAS performance.
- Enable `/app/usdrt/population/utils/mergeMaterials` for stages with many duplicate materials (opt-in; off by default since Kit 108 — route to `fsd-configurator`).
- Consider `/app/usdrt/population/utils/enableRendererInstancing` for heavily-instanced scenes. ⚠️ Experimental, RTX renderer only.
- Author textures at appropriate resolution; consider compressed `.dds` (BC7/BC6H) for delivery.
- Close unused viewports.
- Reduce camera/viewport resolution where the workflow allows.

The deprecated `/app/usdrt/population/utils/instanceCompactTransforms` is intentionally absent from this list — it should not be set on Kit 108+.

## Texture sizing — common partner finding

A common partner finding is **8K textures bound to objects that occupy ≪100 px in the final image**. Match texture resolution to expected on-screen size.

When delivering textures:

- Consider `.dds` (BC7 for color, BC6H for HDR) so source-format conversion costs are paid once at authoring rather than at each load.
- Author at the resolution the object actually needs.

## Do / Don't

- ✅ **DO** leave texture streaming enabled. The RTX renderer streams the appropriate mip levels based on the view.
- ✅ **DO** author textures at appropriate resolution and consider compressed `.dds` at delivery time.
- ✅ **DO** close unnecessary viewports — each one consumes VRAM.
- ✅ **DO** use `.usdc` to reduce system memory usage. Memory-mapped I/O; `.usda` loads entirely into RAM.
- ✅ **DO** update Kit when possible. Memory improvements ship over time and aren't user-configurable. Example: Kit 109+ shares VtArray data zero-copy between USD and Fabric — the same scene takes less RAM after the upgrade. **There is no setting to verify this; updating is the lever.**
- ❌ **DON'T** set thread counts higher than the core count. Over-subscription causes context-switching overhead.
- ❌ **DON'T** invent a "% memory savings" claim for any of these. They aren't citable.

## Things partners commonly try that don't help

- "Verify zero-copy VtArray" — there is no tooling for this. Updating Kit is the lever.
- Setting a `populateAllAuthoredAttributes=0` flag — already the default; don't recommend setting it explicitly.
- Setting `instanceCompactTransforms=1` — deprecated since Kit 108.

## System memory

| Factor | Impact | Mitigation |
|--------|--------|------------|
| FSD Fabric population | Data populated from USD into Fabric | Kit 109+ shares VtArray data zero-copy automatically; updating Kit is the lever |
| High layer count | Each layer kept open in memory | Don't let layer counts grow procedurally; collapse layers during publishing |
| Text `.usda` files | Entire file loaded to RAM | Use `.usdc` (memory-mapped, sparse reads) |
| Full stage loading | All payloads composed | Use payload loading mechanisms — route to `usd-scene-structure` |

## CPU & thread configuration

| Setting | Recommended | Why |
|---------|-------------|-----|
| `carb.tasking.plugin/threadCount` | Match core count (commonly 16 on workstations) | Optimal for most workloads |
| `omni.tbb.globalcontrol/maxThreadCount` | Match thread count | Prevents over-subscription |
| Linux CPU governor | `performance` mode | Maximum clock frequency |

**jemalloc on Linux** is the default on current Linux Kit builds — not a knob users need to configure. Do not recommend setting `LD_PRELOAD=/path/to/jemalloc.so`.

## Asynchronous rendering

- Enabled by default when simulation is paused/stopped.
- Runtime async (experimental): `--/app/asyncRendering=true --/app/omni.usd/asyncHandshake=true`.
- Can improve apparent responsiveness during physics/animation-heavy workloads.

## Source guide section

[`docs/reference/memory-and-resources.md`](../../docs/reference/memory-and-resources.md).

External references: [Optimizing Performance](https://docs.omniverse.nvidia.com/ov/latest/common/performance.html), [SimReady — Materials Best Practices](https://docs.omniverse.nvidia.com/simready/latest/simready-asset-creation/material-best-practices.html), [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html).
