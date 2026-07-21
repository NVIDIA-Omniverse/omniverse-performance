---
description: "GPU and system memory, threading, async rendering, and texture sizing reference"
---

# Memory & Resource Management

GPU memory exhaustion is a common crash cause. System memory mismanagement leads to slow performance long before it crashes. CPU thread configuration can mean the difference between half and full target frame rate.

:::{seealso} Related agentic resource
To measure VRAM and system-memory use across runs, see [OmniPerf](https://github.com/NVIDIA/omniperf) and {doc}`/agentic-resources`.
:::

## Quick reference — Do's and Don'ts

:::{admonition} DO: Leave texture streaming enabled for GPU memory management
:class: tip

The RTX renderer streams the appropriate mip levels based on the view; the budget setting lives in [RTX Common Settings](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html).
:::

:::{admonition} DO: Author textures at appropriate resolution
:class: tip

A common partner finding is 8K textures bound to objects that occupy ≪100 px in the final image. Match texture resolution to expected on-screen size; consider `.dds` (BC7/BC6H) at delivery time so source-format conversion costs are paid once at authoring rather than at each load. Material best practices: [SimReady — Materials](https://docs.omniverse.nvidia.com/simready/latest/simready-asset-creation/material-best-practices.html).
:::

:::{admonition} DO: Close unnecessary viewports
:class: tip

Each viewport consumes VRAM. One fewer viewport = direct memory savings.
:::

:::{admonition} DO: Use `.usdc` to reduce system memory usage
:class: tip

Binary crate format uses memory-mapped I/O. `.usda` loads entirely into RAM. ([OpenUSD File Formats](https://docs.nvidia.com/learn-openusd/latest/stage-setting/usd-file-formats.html))
:::

:::{admonition} DO: Update Kit when you can
:class: tip

Memory improvements ship over time and you don't configure them — for example, Kit 109+ shares VtArray data zero-copy between USD and Fabric, so the same scene takes less RAM after the upgrade. There is no setting to verify; updating is the lever.
:::

:::{admonition} DON'T: Set thread counts higher than your core count
:class: warning

Over-subscription causes context-switching overhead.
:::

## GPU memory checklist

These are bullets, not a priority order — pick the ones that match your bottleneck:

- Enable texture streaming. Loads only the needed mip levels.
- Consider geometry streaming + auto LOD on scenes that exceed GPU memory. Experimental — see {doc}`platform-systems` for caveats and the required restart.
- Enable `/app/usdrt/population/utils/mergeMaterials` for stages with many duplicate materials (opt-in; off by default since Kit 108 — see {doc}`platform-systems`).
- Consider `/app/usdrt/population/utils/enableRendererInstancing` for heavily-instanced scenes. Experimental, RTX renderer only.
- Author textures at appropriate resolution; consider compressed `.dds` for delivery.
- Close unused viewports.
- Reduce camera/viewport resolution where the workflow allows.

The deprecated `instanceCompactTransforms` is intentionally absent from this list — it should not be set on Kit 108+.

## System memory management

| Factor | Impact | Mitigation |
|--------|--------|------------|
| FSD Fabric population | Data populated from USD into Fabric | Kit 109+ shares VtArray data zero-copy automatically; updating Kit is the lever |
| High layer count | Each layer kept open in memory | Don't let layer counts grow procedurally; collapse layers during publishing |
| Text `.usda` files | Entire file loaded to RAM | Use `.usdc` (memory-mapped, sparse reads) |
| Full stage loading | All payloads composed | Use payload loading mechanisms ({doc}`usd-scene-structure`) |

## CPU & thread configuration

| Setting | Recommended | Why |
|---------|-------------|-----|
| `carb.tasking.plugin/threadCount` | Match your core count (commonly 16 on workstation hardware) | Optimal for most workloads |
| `omni.tbb.globalcontrol/maxThreadCount` | Match thread count | Prevents over-subscription |
| Linux CPU governor | `performance` mode | Maximum clock frequency |

Linux memory allocator: jemalloc is the default on current Linux Kit builds; this is not a knob users need to configure.

## Asynchronous rendering

- Enabled by default when simulation is paused/stopped.
- Runtime async (experimental): `--/app/asyncRendering=true --/app/omni.usd/asyncHandshake=true`.
- Can improve apparent responsiveness during physics/animation-heavy workloads.

## Doc references

- [Optimizing Performance](https://docs.omniverse.nvidia.com/ov/latest/common/performance.html)
- [FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)
- [Isaac Sim Performance Optimization Handbook](https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/sim_performance_optimization_handbook.html)
