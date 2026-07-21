# Omniverse Performance — Agent Guide

This repo is a high-level performance guide for **Omniverse Kit** and **OpenUSD**. Use [`README.md`](README.md) for the project overview and [`docs/`](docs/) for the full guide.

When the user clones this repo and points an AI agent at it, treat the `skills/` folder as your first source of truth. Each skill bundles the synthesized Do's, Don'ts, and configuration guidance that has been reviewed and is current as of the most recent revision in [`docs/`](docs/).

## How agents discover this guide

| Agent | Entry point | Notes |
|-------|-------------|-------|
| **OpenAI Codex** (CLI and Web) | This file (`AGENTS.md`) — read natively | Codex's standard convention; nothing else to configure |
| **Claude Code** | `CLAUDE.md` at repo root → redirects here | Claude Code reads `CLAUDE.md` automatically |
| **Cursor** | `.cursor/rules/performance-self-serve.mdc` → links here | Cursor's "Project Rules" format; auto-applied to all conversations in this repo |

Whatever agent loads this file: same routing table below, same working principles, same skills folder. The three agents converge here.

## When to use which skill

Before answering requests in these areas, read the matching project skill. (Editing or building the guide itself, rather than using it? See [`AUTHORING.md`](AUTHORING.md).)

| If the user is asking about… | Read |
|------------------------------|------|
| "My scene is slow", initial triage, where to start | `skills/perf-triage/SKILL.md` |
| Architecting from scratch, data model vs. runtime vs. wire, what belongs in USD vs. downstream | `docs/get-started/architecting-for-performance.md` (chapter — no dedicated skill) |
| Profiling, F8, Tracy, activity timeline, finding the bottleneck | `skills/profiling-guide/SKILL.md` |
| Payloads, layers, instancing, file formats, USD asset structure | `skills/usd-scene-structure/SKILL.md` |
| USDRT, Fabric, stage queries, `TfNotice`, change tracking, `UsdWatcher` | `skills/usdrt-advisor/SKILL.md` |
| Scene Optimizer, merge/decimate/dedupe, performance validators | `skills/scene-optimizer-guide/SKILL.md` |
| RTX modes, DLSS, glass, render settings, multi-GPU | `skills/rendering-tuner/SKILL.md` |
| FSD, Fabric Scene Delegate, `mergeMaterials`, `enableRendererInstancing` | `skills/fsd-configurator/SKILL.md` |
| UJITSO, derived-data cache, "first load is slow", cache warmup | `skills/ujitso-manager/SKILL.md` |
| GPU memory, VRAM, system RAM, threading, texture sizing | `skills/memory-optimizer/SKILL.md` |
| CAD import, validation, materials pipeline, physics colliders | `skills/content-prep-advisor/SKILL.md` |
| Cloud deployment, container cold start, NVCF, OKAS, K8s | `skills/cloud-perf-advisor/SKILL.md` |
| GPU crashes, "device-lost", performance regression after Kit upgrade | `skills/troubleshooting-router/SKILL.md` |

## How the skills compose

The skills are designed to chain. A typical flow:

```
perf-triage → profiling-guide → <topic skill> → troubleshooting-router (if needed)
```

Most user requests start at `perf-triage`. The triage skill identifies whether the issue is loading time, FPS, memory, or a crash, then names which topic skill to read next.

## When to hand off to the USD Performance Tuning skill

The [USD Performance Tuning skill](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) is the agentic companion for **headless, library-level work on the USD files themselves** — diagnosing and optimizing a stage independent of whether it ever runs in a Kit app. It is a top-level workflow: baseline-profile → assess composition → validate → restructure → apply Scene Optimizer operations → re-profile → write a report.

Hand off when:

- The task is **"fix the USD"** — author smarter structure, optimize a stage on disk, run Scene Optimizer or validators headlessly — and a running Kit app is not required to do the work.
- The user wants an **end-to-end, agent-driven optimization pass** with before/after profiling and a written report, rather than the targeted "what and why" this repo's skills provide.
- The work is **standalone OpenUSD** with no Kit runtime, FSD, UJITSO, or rendering in scope.

Keep using this repo's skills when the question is about the **running Kit application** — USDRT/Fabric at runtime, FSD, UJITSO, rendering, platform systems — or when the user wants the concise *what and why* rather than an automated mutation pass. The two are complementary: this guide explains the decision; the skill can execute it on the files. The skills follow the same single-file `SKILL.md` shape used here, under [`skills/`](https://github.com/NVIDIA/skills/tree/main/skills) in the [NVIDIA/skills](https://github.com/NVIDIA/skills) repo.

**The engines also run standalone, without Kit.** Both tools this guide leans on are available as Kit-independent libraries you can drop into a headless pipeline or CI gate — which is what makes the "fix the USD" path above practical without a Kit runtime:

- **Asset Validator** — `pip install usd-validation-nvidia` ([PyPI](https://pypi.org/project/usd-validation-nvidia/), [docs](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html)). Pure-Python, the same engine as the in-Kit Asset Validator, with a CLI (`nvidia_usd_validate`) and Python API. Ready to wire into CI today. Use this package; the older `omniverse-asset-validator` is frozen.
- **Scene Optimizer** — the [`usd-optimize`](https://github.com/NVIDIA-Omniverse/usd-optimize) repo packages the optimization operations as an embeddable C++/Python library that runs without Omniverse Kit. **Caveat:** it is build-from-source (or prebuilt binaries), is not currently accepting contributions, and makes no parity guarantee with the in-Kit Scene Optimizer — treat it as the advanced/embedding path, not a drop-in replacement. For most "fix the USD" work, the in-Kit Scene Optimizer or the agentic skill above is still the path.

## When to hand off to Omniperf

[Omniperf](https://github.com/NVIDIA/omniperf) is the operational companion repo. Hand off when:

- The user is on **Isaac Sim** or **Isaac Lab** specifically — Omniperf has install, benchmark, and trace-capture skills tuned for those workloads.
- The user needs to **install a profiler** (Nsight Systems, Tracy, csvexport, sqlite3) — point at [`install-profilers`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/install-profilers/SKILL.md).
- The user needs to **capture** a Tracy or `nsys` trace, or apply the **COLD/WARM/TRACY** measurement methodology — point at [`profiling`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/profiling/SKILL.md). The skills in this repo cover *when and why* to profile; Omniperf covers *how to actually capture and analyze*.
- The user needs **reference benchmark numbers** (per-GPU, per-commit FPS, GPU utilization, memory, startup time) — point at the [Omniperf dashboards](https://nvidia.github.io/omniperf/). This guide does not publish specific numbers; the dashboards are the citable source.
- The user wants to **compare two runs** of the same workload — point at [`nsys-analyze`](https://github.com/NVIDIA/omniperf/blob/main/.agents/skills/nsys-analyze/SKILL.md).

The Omniperf skills live under [`.agents/skills/`](https://github.com/NVIDIA/omniperf/tree/main/.agents/skills) and follow the same single-file `SKILL.md` shape used here.

## Working principles encoded in these skills

These appear in every skill — match the same conventions when responding to the user:

1. **Always recommend reproducing against the latest Kit (109/110) and the stock Kit App Template first.** Many issues are already fixed upstream.
2. **Defaults-first.** Recommend that users keep defaults unless they have a specific reason. When a setting must be changed, recommend leaving a comment in the `.kit` file explaining why.
3. **No invented numbers.** Never quote a specific FPS, prim-count threshold, scaling factor, or % improvement unless it has a citable source. Prefer qualitative wording.
4. **No customer attribution.** Don't name specific partners or customers when describing scenarios. Generic descriptions only.
5. **Doc links inline next to claims.** When citing documentation, place the link next to the statement it supports — not in a footer.
6. **Mark experimental and deprecated explicitly.** The inline `⚠️ Experimental` / `🗑️ Deprecated` markers are fine in the plain-markdown skills. Editing the rendered Sphinx docs? See [`AUTHORING.md`](AUTHORING.md) for the text-only admonition-title convention (the double-icon bug).

## Document layout

The repository structure, Sphinx build, conventions, link validation, and git workflow are documented in [`AUTHORING.md`](AUTHORING.md) — read it before editing or building the guide. After consulting a skill, follow the link from the skill's "Source guide section" line to the canonical chapter in `docs/` if the user needs more depth.

## Behavior expectations

- **Do** quote specific setting paths verbatim (e.g. `/app/usdrt/population/utils/mergeMaterials`, never just `mergeMaterials`).
- **Do** flag when guidance depends on Kit version. Most defaults assume Kit 109 / 110.
- **Don't** fabricate code samples — the runnable examples in `skills/usdrt-advisor/SKILL.md` and `docs/reference/usd-in-kit.md` are intentionally complete (with imports). Copy from those rather than inventing variants.
- **Don't** invoke skills not listed in this file. If the user's question doesn't fit any skill, answer directly using the canonical chapter in `docs/`.

