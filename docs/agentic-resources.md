---
description: "Agentic performance resources: how this guide (the trunk) connects out to specialized AI skills and tools for Omniverse and OpenUSD performance"
---

# Agentic Resources

This guide is the **trunk**: the single entry point for performance work on Omniverse Kit and OpenUSD. It holds the concise, generally-true Do's and Don'ts and points out to the specialized resources — the **branches** — that go deep on one area.

Performance tooling at NVIDIA is spread across several repos and docs sites. If you land in one of them first, you can lose the bigger picture; if you start here, this page is the map back out. Each branch below is maintained by its own team — treat it as the authority for its area.

## Agentic skills

These are installable AI agent skills. Point your coding agent (Claude Code, Cursor, Codex, or any MCP-capable harness) at the repo and it can apply the guidance directly rather than you reading and translating it by hand.

:::{seealso} USD Performance Tuning skills
The agentic companion to this guide for **OpenUSD authoring and scene work** — the headless, library-level path that operates on USD files directly.

- [omniverse-usd-performance-tuning](https://github.com/NVIDIA/skills/tree/main/skills/omniverse-usd-performance-tuning) — clone or install into your agent harness.

Use it when the work is "fix the USD," independent of whether the scene ever runs in Kit.
:::

:::{seealso} Omniperf — operational profiling and benchmarking
The operational *how*: installing profilers, running canonical Isaac Sim and Isaac Lab benchmarks, capturing Tracy and Nsight traces, and comparing runs to prove a change actually moved the number.

- [Omniperf](https://github.com/NVIDIA/omniperf) — the repo.
- [Agent skills](https://github.com/NVIDIA/omniperf/tree/main/.agents/skills) — the same single-file `SKILL.md` shape used here.
- [Reference benchmark dashboards](https://nvidia.github.io/omniperf/) — measured FPS, GPU utilization, memory, and startup times by GPU and commit.

Use it when you need a measurable before/after rather than a qualitative recommendation.
:::

## Both worlds: docs and skills

You do not need an agent to use this guide. Every section leads with Do's and Don'ts that read fine as plain documentation, and links out to the official source for the *why*. Where an agentic skill exists for a section, a short pointer at the top of that page names it — so an agent can pick it up automatically, and a human reading the page knows the skill is there.

If you have an agentic harness with budget to spend, prefer the skills: they stay closer to the source of truth and can act. If you don't, the documentation mirrors the same guidance.

## This guide's own skill tree

This repo also ships a companion skill tree that maps each guide section to a bounded skill. See {doc}`skill-tree/index` for the skill list and how they chain. The skill tree is wired for Claude Code, Cursor, and Codex (see the repo `README`).

