---
description: "High-level performance guide for Omniverse Kit and OpenUSD: profiling, scene structure, FSD/UJITSO, rendering, troubleshooting"
---

# Omniverse Performance

Diagnose, explain, and fix performance issues in Omniverse Kit and OpenUSD applications — loading times, FPS, memory usage, and cloud deployment bottlenecks.

Each section leads with actionable Do's and Don'ts. The deeper explanation and links to official documentation sit next to the guidance they support, not in a footer. Where a recommendation is experimental, deprecated, or version-dependent, that fact is called out in line.

Defaults assume **Kit 109 or 110**. Older releases (107 and earlier) are end-of-life or near it; if you are on an older branch, expect some defaults and behaviors to differ.

This guide is the **trunk** for Omniverse and OpenUSD performance — the concise, generally-true guidance — and it links out to specialized resources (agentic skills, OmniPerf, the official docs) for depth. If you work with an AI coding agent, see {doc}`agentic-resources` for the installable skills that apply this guidance directly.

## Choose your path

Two questions route most of this guide. Answer them first.

```{mermaid}
flowchart TD
    start["What are you tuning?"] --> w{"Where does the work live?"}
    w -->|"Pure OpenUSD files<br/>(headless, library-level)"| usd["Author smarter USD:<br/>scene structure, payloads,<br/>instancing, file formats"]
    w -->|"Inside a Kit app / at runtime"| kit["Kit & runtime path:<br/>USDRT/Fabric, FSD, rendering,<br/>platform systems"]
    usd --> usddocs["USD Scene Structure +<br/>USD Performance Tuning skill"]
    kit --> stage{"Loading or running?"}
    stage -->|"Slow to load"| load["Scene structure, UJITSO,<br/>file formats, caching"]
    stage -->|"Slow once loaded (FPS)"| run["Profile first, then USDRT,<br/>rendering, scene optimization"]
```

The pure-USD path is library-level work on the files themselves — it pays off no matter how the scene is later consumed, and it's where the {doc}`agentic-resources` USD Performance Tuning skill helps most. The Kit/runtime path is about how a live application loads and renders that data. **Loading performance comes first**: a scene that is slow to load frustrates users before frame rate ever matters; runtime FPS is the next priority, then conversion/throughput.

If you're not sure which path you're on, start with {doc}`get-started/profiling` — it tells you where the time is actually going.

## Get Started

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item-card} {octicon}`milestone;1.5em;sd-mr-1` Architecting for Performance
:link: get-started/architecting-for-performance
:link-type: doc

First-principles framing for architects — access patterns, the data-model / runtime / wire split, what belongs in USD vs. downstream.
:::

:::{grid-item-card} {octicon}`rocket;1.5em;sd-mr-1` Quick Start
:link: get-started/quick-start
:link-type: doc

Settings checklist, essential launch flags, and your first five minutes with a new scene.
:::

:::{grid-item-card} {octicon}`search;1.5em;sd-mr-1` Profiling
:link: get-started/profiling
:link-type: doc

F8, Tracy, the activity timeline — find the bottleneck before tuning anything else.
:::

:::{grid-item-card} {octicon}`dependabot;1.5em;sd-mr-1` Agentic Resources
:link: agentic-resources
:link-type: doc

The trunk→branch map: installable AI skills, OmniPerf, and how the docs and skills fit together.
:::

:::{grid-item-card} {octicon}`book;1.5em;sd-mr-1` Conventions
:link: about/conventions
:link-type: doc

Callouts, and what "Experimental" or "Deprecated" mean in this guide.
:::

::::

## Diagnose by symptom

::::{grid} 1 2 2 4
:gutter: 2

:::{grid-item-card} Slow scene loading
:link: workflows/troubleshooting
:link-type: doc

File format, layer count, payloads, UJITSO, network.
:::

:::{grid-item-card} Low FPS during navigation
:link: workflows/troubleshooting
:link-type: doc

Profile first; route to rendering, scene optimizer, or USDRT.
:::

:::{grid-item-card} GPU crash / device-lost
:link: workflows/troubleshooting
:link-type: doc

Driver check first, then UJITSO cache, VRAM budget, USD validity.
:::

:::{grid-item-card} Performance regression after a Kit upgrade
:link: workflows/troubleshooting
:link-type: doc

Default flips, deprecated flags, divergence from the stock template.
:::

::::

## Configure and tune

::::{grid} 1 2 2 3
:gutter: 2

:::{grid-item-card} {octicon}`stack;1.5em;sd-mr-1` USD Scene Structure
:link: reference/usd-scene-structure
:link-type: doc

Payloads, layers, instancing, file formats — the authoring decisions that compound.
:::

:::{grid-item-card} {octicon}`code;1.5em;sd-mr-1` USD in Kit (USDRT)
:link: reference/usd-in-kit
:link-type: doc

Stage queries, change tracking, and Fabric — the patterns most developers miss.
:::

:::{grid-item-card} {octicon}`tools;1.5em;sd-mr-1` Scene Optimization
:link: workflows/scene-optimization
:link-type: doc

Bottleneck-driven choice between merging, decimating, deduplicating.
:::

:::{grid-item-card} {octicon}`paintbrush;1.5em;sd-mr-1` Rendering Performance
:link: reference/rendering-performance
:link-type: doc

RTX modes, DLSS, glass, multi-GPU — the renderer-side levers.
:::

:::{grid-item-card} {octicon}`cpu;1.5em;sd-mr-1` Platform Systems
:link: reference/platform-systems
:link-type: doc

FSD, UJITSO, streaming, and the Omniverse cache landscape.
:::

:::{grid-item-card} {octicon}`database;1.5em;sd-mr-1` Memory & Resources
:link: reference/memory-and-resources
:link-type: doc

GPU VRAM, system RAM, threading, texture sizing.
:::

::::

## Pipeline and deployment

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item-card} {octicon}`workflow;1.5em;sd-mr-1` Content Preparation
:link: workflows/content-preparation
:link-type: doc

CAD import, validation, materials, physics — preventing issues at the source.
:::

:::{grid-item-card} {octicon}`cloud;1.5em;sd-mr-1` Cloud Deployment
:link: workflows/cloud-deployment
:link-type: doc

Caching architecture, pre-warming strategy, container considerations.
:::

::::

## AI Skill Tree

The companion skill tree maps each guide section to a bounded AI agent skill. See {doc}`skill-tree/index` for the skill list and how they chain, and {doc}`agentic-resources` for the external skills this guide points out to (USD performance tuning, Omniperf).

:::{admonition} Operational companion: Omniperf
:class: tip dropdown

This guide covers the *what* and *why* of performance work on Kit and OpenUSD. For the operational *how* — installing profilers, running canonical Isaac Sim and Isaac Lab benchmarks, capturing Tracy and Nsight traces with the COLD/WARM/TRACY methodology, and comparing runs — see [**Omniperf**](https://github.com/NVIDIA/omniperf).

- [Agent skills](https://github.com/NVIDIA/omniperf/tree/main/.agents/skills) — same single-file `SKILL.md` shape used here
- [Profiling guide](https://github.com/NVIDIA/omniperf/blob/main/dev/docs/profiling-guide.md) — Carbonite profiler subsystem internals
- [Reference benchmark dashboards](https://nvidia.github.io/omniperf/) — measured FPS, GPU utilization, memory, and startup times by GPU and commit
:::

:::{seealso}
- [SimReady](https://docs.omniverse.nvidia.com/simready/latest/overview.html) — SimReady specification and asset creation
- [VFI Guide](https://docs.omniverse.nvidia.com/vfi/latest/index.html) — Virtual Facility Integration workflow
- [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) — Reproduce against the stock template
- [Omniperf](https://github.com/NVIDIA/omniperf) — operational companion for Isaac Sim, Isaac Lab, and Kit-based apps

**Key extensions referenced by this guide**

- [FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html)
- [UJITSO Cache System](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html)
- [Scene Optimizer](https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer.html)
- [Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html)
- [Profiler Window](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler.html)
- [Tracy Profiler](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler_tracy.html)
:::

```{toctree}
:hidden:

Home <self>
agentic-resources
```

```{toctree}
:caption: About
:hidden:

about/conventions
about/kit-version-targeting
```

```{toctree}
:caption: Get Started
:hidden:

get-started/architecting-for-performance
get-started/quick-start
get-started/profiling
```

```{toctree}
:caption: Workflows
:hidden:

workflows/scene-optimization
workflows/content-preparation
workflows/cloud-deployment
workflows/troubleshooting
```

```{toctree}
:caption: Reference
:hidden:

reference/usd-scene-structure
reference/usd-in-kit
reference/rendering-performance
reference/platform-systems
reference/memory-and-resources
reference/sources
```

```{toctree}
:caption: AI Skill Tree
:hidden:

Overview <skill-tree/index>
skill-tree/manifest
skill-tree/reference/fsd-settings
skill-tree/reference/ujitso-settings
skill-tree/reference/render-settings
skill-tree/reference/scene-optimizer-ops
skill-tree/reference/troubleshooting-scenarios
```
