# Omniverse Performance

A high-level performance guide for developers building on **Omniverse Kit** and **OpenUSD**. Use it to diagnose, explain, or fix performance issues — slow loading times, low FPS during navigation, GPU crashes, memory exhaustion, and cloud deployment cold-starts.

The guide is a curated set of Do's, Don'ts, decision trees, and configuration tables that recur across customer escalations.

This guide is the **trunk** for Omniverse and OpenUSD performance — the concise, generally-true guidance — and it links out to specialized **branch** resources for depth: the [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) for headless, library-level work on USD files, and [Omniperf](https://github.com/NVIDIA/omniperf) for operational profiling and benchmarking.

## Documentation

**[Read the published guide](https://nvidia-omniverse.github.io/omniverse-performance/)** — organized by topic, with everything below just a click in.

> **Defaults assume Kit 109 or 110.** Older releases (107 and earlier) are end-of-life or near it. The single most useful first step when investigating any performance issue is to reproduce against the latest Kit and a stock [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template).

## Who this is for

- **Developers** building Kit applications who hit a perf cliff at scale
- **Solution architects** triaging customer escalations
- **Pipeline engineers** preparing content for digital twin and AI Factory workloads
- **Isaac Sim and Isaac Lab users** — this guide covers the Kit/USD layer underneath; the operational companion for install, benchmarking, and trace capture on Isaac is [Omniperf](https://github.com/NVIDIA/omniperf)
- **Anyone optimizing USD files headlessly** (library-level, no running Kit app) — the agentic companion that operates directly on the files is the [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning)
- **Anyone using an AI coding assistant** — clone the repo, point Claude Code, Cursor, or Codex at it, and the [skills](#use-with-an-ai-assistant) auto-load
- **AI agent authors** integrating performance-aware skills into their workflow ([AI Skill Tree](https://nvidia-omniverse.github.io/omniverse-performance/skill-tree/index.html))

## What's covered

| Area | Read |
|------|------|
| Five-minute checklist before reaching for the profiler | [Quick Start](https://nvidia-omniverse.github.io/omniverse-performance/get-started/quick-start.html) |
| Profiling — F8, Tracy, activity timeline, decision tree | [Profiling](https://nvidia-omniverse.github.io/omniverse-performance/get-started/profiling.html) |
| USD scene structure: payloads, layers, instancing, file formats | [USD Scene Structure](https://nvidia-omniverse.github.io/omniverse-performance/reference/usd-scene-structure.html) |
| USDRT, Fabric, change tracking — runnable code samples | [USD in Kit](https://nvidia-omniverse.github.io/omniverse-performance/reference/usd-in-kit.html) |
| Bottleneck-driven Scene Optimizer workflow | [Scene Optimization](https://nvidia-omniverse.github.io/omniverse-performance/workflows/scene-optimization.html) |
| Rendering: RTX modes, DLSS, glass, multi-GPU | [Rendering Performance](https://nvidia-omniverse.github.io/omniverse-performance/reference/rendering-performance.html) |
| FSD, UJITSO, streaming, the Omniverse cache landscape | [Platform Systems](https://nvidia-omniverse.github.io/omniverse-performance/reference/platform-systems.html) |
| GPU/system memory, threading, texture sizing | [Memory & Resources](https://nvidia-omniverse.github.io/omniverse-performance/reference/memory-and-resources.html) |
| CAD import, validation, materials, physics | [Content Preparation](https://nvidia-omniverse.github.io/omniverse-performance/workflows/content-preparation.html) |
| Cloud caching architecture and pre-warming | [Cloud Deployment](https://nvidia-omniverse.github.io/omniverse-performance/workflows/cloud-deployment.html) |
| Common scenarios with step-by-step resolution + hardware/driver checks | [Troubleshooting](https://nvidia-omniverse.github.io/omniverse-performance/workflows/troubleshooting.html) |
| Source documentation index | [Source Index](https://nvidia-omniverse.github.io/omniverse-performance/reference/sources.html) |
| Companion AI skill tree (human-readable companion to the 12 skills) | [AI Skill Tree](https://nvidia-omniverse.github.io/omniverse-performance/skill-tree/index.html) |

## Use with an AI assistant

The repo ships a working set of agent skills. Clone the repo, point an AI assistant at the folder, and it picks up the routing automatically — no extra configuration on your end.

### Supported assistants

| Assistant | Discovery file | Auto-applies? |
|-----------|----------------|---------------|
| **OpenAI Codex** (CLI and Web) | [`AGENTS.md`](AGENTS.md) | ✅ Codex reads `AGENTS.md` natively at session start |
| **Claude Code** | [`CLAUDE.md`](CLAUDE.md) → redirects to `AGENTS.md` | ✅ Claude Code reads `CLAUDE.md` automatically |
| **Cursor** | [`.cursor/rules/performance-self-serve.mdc`](.cursor/rules/performance-self-serve.mdc) | ✅ Cursor's "Project Rules" — `alwaysApply: true` injects on every conversation in this repo |

All three converge on the same routing table in [`AGENTS.md`](AGENTS.md), the same working principles, and the same skills folder.

### What lives in [`skills/`](skills/)

Twelve self-contained skills, each covering one area:

| Skill | Use when the question is about… |
|-------|----------------------------------|
| [`perf-triage`](skills/perf-triage/SKILL.md) | Initial triage — "my scene is slow", routing to a specialist skill |
| [`profiling-guide`](skills/profiling-guide/SKILL.md) | F8, Tracy, the activity timeline, finding the bottleneck |
| [`usd-scene-structure`](skills/usd-scene-structure/SKILL.md) | Payloads, layers, instancing, file formats, prim count |
| [`usdrt-advisor`](skills/usdrt-advisor/SKILL.md) | USDRT migration, change tracking, complete runnable code samples |
| [`scene-optimizer-guide`](skills/scene-optimizer-guide/SKILL.md) | Bottleneck-driven Scene Optimizer — operations, validators |
| [`rendering-tuner`](skills/rendering-tuner/SKILL.md) | RTX modes, DLSS, glass, multi-GPU |
| [`fsd-configurator`](skills/fsd-configurator/SKILL.md) | FSD, the `mergeMaterials` default (off by default since Kit 108), deprecated flags |
| [`ujitso-manager`](skills/ujitso-manager/SKILL.md) | UJITSO derived-data cache, "first load is slow" |
| [`memory-optimizer`](skills/memory-optimizer/SKILL.md) | GPU/system memory, threading, texture sizing |
| [`content-prep-advisor`](skills/content-prep-advisor/SKILL.md) | CAD import, validation, materials, physics colliders |
| [`cloud-perf-advisor`](skills/cloud-perf-advisor/SKILL.md) | Cloud deployment, container cold starts, NVCF/OKAS/UCC |
| [`troubleshooting-router`](skills/troubleshooting-router/SKILL.md) | GPU crashes, regressions after Kit upgrade, common scenarios |

## Conventions

- ✅ **DO** — recommended action
- ❌ **DON'T** — common pitfall to avoid
- ⚠️ **Experimental** — may change between Kit releases or has known trade-offs
- 🗑️ **Deprecated** — should no longer be used; strip from your `.kit` files

## Related

**Companions** — this guide is the *what and why*; reach for these for depth:

- [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) — agentic companion for **headless USD file** work: it *executes* structure and optimization changes on a stage (Scene Optimizer, validators), where this guide explains what to change and why.
- [Omniperf](https://github.com/NVIDIA/omniperf) — the **operational** counterpart: install profilers, capture Tracy/Nsight traces, run Isaac Sim / Isaac Lab benchmarks, and compare runs, with [measured benchmark dashboards](https://nvidia.github.io/omniperf/) per GPU and commit.

**Also useful:**

- [Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) — the recommended baseline for reproducing performance issues against the stock template.
- [SimReady](https://docs.omniverse.nvidia.com/simready/latest/overview.html) — SimReady specification and asset creation.
- [VFI Guide](https://docs.omniverse.nvidia.com/vfi/latest/index.html) — Virtual Facility Integration workflow.
- [aif-pipeline-samples](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples) — CAD-to-USD pipeline samples.

## License

Dual-licensed — docs and skills under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/), code under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). See [`LICENSE`](LICENSE).
