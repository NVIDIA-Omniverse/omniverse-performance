---
description: "The 12 AI agent skills aligned to the Omniverse Performance guide — what each covers, how they chain, and the chapter each draws from"
---

# AI Skill Tree

The repo ships **12 self-contained skills** under `skills/<name>/SKILL.md`. An AI agent loads them to give context-aware Omniverse and USD performance advice, chaining them as a problem is narrowed down. This section is the human-readable companion: what each skill covers, how they fit together, and which guide chapter each draws from. The agent-facing routing lives in the repo's `AGENTS.md`.

## Sections

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item-card} {octicon}`list-unordered;1.5em;sd-mr-1` Skill Manifest
:link: manifest
:link-type: doc

Each skill with the topics that route to it, the guide chapter it draws from, and what it does.
:::

:::{grid-item-card} {octicon}`database;1.5em;sd-mr-1` Reference Data
:link: reference/fsd-settings
:link-type: doc

Settings tables, operations, and scenarios that individual skills draw on.
:::

::::

## Design principles

1. **Each skill solves a clear, bounded problem** — "my scene is slow" activates the right skill.
2. **Skills compose naturally** — diagnose → optimize → validate.
3. **Progressive depth** — quick checklist for newcomers, deep tuning for experts, same entry point.
4. **Knowledge is sourced and current** — each skill bundles specific doc links and reference data.
5. **Dual-purpose** — the same content serves both the AI agent skills and this human-readable documentation.
6. **Default-first** — recommend defaults; only suggest changing a setting when there is a concrete reason.
7. **No invented numbers** — when reference numbers don't exist in published docs, give qualitative guidance and link the source.
8. **No customer attribution** — scenarios are described without naming specific partners or customers.

## The skills

```
skills/
├── perf-triage/SKILL.md            ← entry point: classify the problem, route onward
├── profiling-guide/SKILL.md        ← F8, Tracy, activity timeline — find the bottleneck
├── usd-scene-structure/SKILL.md    ← payloads, layers, instancing, file formats
├── usdrt-advisor/SKILL.md          ← USDRT / Fabric queries, change tracking
├── scene-optimizer-guide/SKILL.md  ← bottleneck-driven Scene Optimizer workflow
├── rendering-tuner/SKILL.md        ← RTX modes, DLSS, glass, multi-GPU
├── fsd-configurator/SKILL.md       ← Fabric Scene Delegate settings (defaults-first)
├── ujitso-manager/SKILL.md         ← UJITSO derived-data cache
├── memory-optimizer/SKILL.md       ← GPU/system memory, threading, texture sizing
├── content-prep-advisor/SKILL.md   ← CAD import, validation, materials, physics
├── cloud-perf-advisor/SKILL.md     ← cloud caching, cold start, containers
└── troubleshooting-router/SKILL.md ← crashes, regressions, scenario routing
```

## Routing

`perf-triage` is the entry point for any performance question. It applies the first-step checks, classifies the symptom, and routes to the specialist skill.

| If the question is about… | Skill |
|---------------------------|-------|
| "My scene is slow", initial triage, where to start | `perf-triage` |
| Profiling, F8, Tracy, activity timeline, finding the bottleneck | `profiling-guide` |
| Payloads, layers, instancing, file formats, USD asset structure | `usd-scene-structure` |
| USDRT, Fabric, stage queries, `TfNotice`, change tracking, `UsdWatcher` | `usdrt-advisor` |
| Scene Optimizer, merge / decimate / dedupe, performance validators | `scene-optimizer-guide` |
| RTX modes, DLSS, glass, render settings, multi-GPU | `rendering-tuner` |
| FSD, Fabric Scene Delegate, `mergeMaterials`, `enableRendererInstancing` | `fsd-configurator` |
| UJITSO, derived-data cache, "first load is slow", cache warmup | `ujitso-manager` |
| GPU memory, VRAM, system RAM, threading, texture sizing | `memory-optimizer` |
| CAD import, validation, materials pipeline, physics colliders | `content-prep-advisor` |
| Cloud deployment, container cold start, NVCF, OKAS, K8s | `cloud-perf-advisor` |
| GPU crashes, "device-lost", performance regression after a Kit upgrade | `troubleshooting-router` |

**Chaining.** A typical flow is `perf-triage` → `profiling-guide` → the topic skill → `troubleshooting-router` (if needed). If a request spans multiple areas, chain in logical order: diagnose first, then optimize, then validate.

## Mapping to guide sections

| Skill | Guide section |
|-------|---------------|
| `perf-triage` | {doc}`/get-started/quick-start`, {doc}`/get-started/profiling`, {doc}`/workflows/troubleshooting` |
| `profiling-guide` | {doc}`/get-started/profiling` |
| `usd-scene-structure` | {doc}`/reference/usd-scene-structure` |
| `usdrt-advisor` | {doc}`/reference/usd-in-kit` |
| `scene-optimizer-guide` | {doc}`/workflows/scene-optimization` |
| `rendering-tuner` | {doc}`/reference/rendering-performance` |
| `fsd-configurator`, `ujitso-manager` | {doc}`/reference/platform-systems` |
| `memory-optimizer` | {doc}`/reference/memory-and-resources` |
| `content-prep-advisor` | {doc}`/workflows/content-preparation` |
| `cloud-perf-advisor` | {doc}`/workflows/cloud-deployment` |
| `troubleshooting-router` | {doc}`/workflows/troubleshooting` |
