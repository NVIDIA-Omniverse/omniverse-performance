---
description: "The 12 skills — the topics that route to each, the guide chapter it draws from, and what it does"
---

# Skill Manifest

Each skill maps a set of user topics to a bounded part of the guide. An agent uses these to route a question to the right skill; a reader can use it as an index of what the skill set covers. The skills are deliberately a synthesis of the Do's, Don'ts, and decision tables in the matching `docs/` chapters — the chapters carry the depth.

## Diagnostics & triage

### `perf-triage`
**Use when:** "my scene is slow", "low FPS", "scene takes forever to load", "GPU crash", "out of memory", or you don't yet know where to start.
**Guide source:** {doc}`/get-started/quick-start`, {doc}`/get-started/profiling`, {doc}`/workflows/troubleshooting`
**What it does:** Applies the three first-step checks (latest Kit, stock app template, GPU driver), classifies the problem as loading / FPS / memory / crash, then routes to the specialist skill.

### `profiling-guide`
**Use when:** "how to profile", "where's the bottleneck", "F8", "Tracy", "activity timeline", "GPU usage", "load-time profile".
**Guide source:** {doc}`/get-started/profiling`
**What it does:** Walks through profiler selection, trace capture, and result interpretation. Confirms the `omni.kit.profiler.window` and `omni.kit.profiler.tracy` extensions are loaded.

## USD authoring

### `usd-scene-structure`
**Use when:** "payload", "sublayer vs reference", "layer count", "instanceable", "point instancer", "prim count", "USDZ", "USDA vs USDC", "scene is heavy".
**Guide source:** {doc}`/reference/usd-scene-structure`
**What it does:** Payloads for heavy geometry, binary `.usdc` for data-heavy files, layer hygiene, the instancing caveat (only helps on referenced/payloaded assets), and choosing the simplest composition arc that fits.

## USD in Kit

### `usdrt-advisor`
**Use when:** "USDRT", "Fabric", "stage traversal slow", "TfNotice", "stage query", "change tracking", "UsdWatcher", "Python performance in Kit".
**Guide source:** {doc}`/reference/usd-in-kit`
**What it does:** Migrates Python traversal to USDRT queries and `TfNotice` to USDRT change tracking or `UsdWatcher`, with complete runnable code samples.

## Scene optimization

### `scene-optimizer-guide`
**Use when:** "Scene Optimizer", "optimize scene", "merge meshes", "decimate", "deduplicate", "reduce triangles", "performance validators".
**Guide source:** {doc}`/workflows/scene-optimization` (reference: {doc}`reference/scene-optimizer-ops`)
**What it does:** Bottleneck-first operation selection (memory / FPS / load-time / visual artifacts). Warns that merging meshes is counter-productive on instanced or geo-streamed content.

## Rendering

### `rendering-tuner`
**Use when:** "which renderer", "RT 2.0 vs path tracing", "render settings", "bounces", "samples per pixel", "DLSS", "frame generation", "glass performance", "multi-GPU".
**Guide source:** {doc}`/reference/rendering-performance` (reference: {doc}`reference/render-settings`)
**What it does:** Renderer choice, bounce and sampling tuning, DLSS, thin-walled glass, and multi-GPU — leading with a check that the workload is not CPU-bound first.

## Platform systems

### `fsd-configurator`
**Use when:** "Fabric Scene Delegate", "FSD", "Fabric", "Hydra population", "mergeMaterials", "renderer instancing".
**Guide source:** {doc}`/reference/platform-systems` (reference: {doc}`reference/fsd-settings`)
**What it does:** Defaults-first. Surfaces only the small set of FSD population flags partners need to consider, and recommends commenting any changed setting in the `.kit` file with the reason.

### `ujitso-manager`
**Use when:** "UJITSO", "derived-data cache", "first load is slow", "cache warmup".
**Guide source:** {doc}`/reference/platform-systems` (reference: {doc}`reference/ujitso-settings`)
**What it does:** UJITSO configuration and cache warmup so repeat loads are fast.

## Memory & resources

### `memory-optimizer`
**Use when:** "GPU memory", "VRAM", "out of GPU memory", "system RAM", "memory leak", "CPU bottleneck", "thread count", "texture sizing".
**Guide source:** {doc}`/reference/memory-and-resources`
**What it does:** GPU VRAM and system RAM budgeting, threading, and texture sizing.

## Content pipeline

### `content-prep-advisor`
**Use when:** "import CAD", "CAD to USD", "validate USD", "asset validator", "usdchecker", "material pipeline", "colliders", "PhysX", "DDS texture".
**Guide source:** {doc}`/workflows/content-preparation`
**What it does:** Validation-tool selection, CAD import, materials, and physics colliders — fixing issues at the source where possible.

## Cloud

### `cloud-perf-advisor`
**Use when:** "cloud performance", "container startup", "cold start", "K8s profiling", "cloud caching", "NVCF", "OKAS", "UCC".
**Guide source:** {doc}`/workflows/cloud-deployment`
**What it does:** Caching architecture, pre-warming strategy, and container cold-start considerations.

## Troubleshooting

### `troubleshooting-router`
**Use when:** "GPU crash", "device-lost", "performance regression after a Kit upgrade", or a symptom that matches a known scenario.
**Guide source:** {doc}`/workflows/troubleshooting` (reference: {doc}`reference/troubleshooting-scenarios`)
**What it does:** Driver-check-first scenario routing for crashes, regressions, and other common failure patterns.

## Doc-only chapters (no skill)

Some guide chapters are read directly rather than through a skill — the routing table in `AGENTS.md` points to them.

### `architecting-for-performance`
**Use when:** "how should I structure this from scratch", "data model vs. runtime vs. wire", "what belongs in USD vs. downstream", first-principles design questions.
**Guide source:** {doc}`/get-started/architecting-for-performance`
**Why no skill:** It is first-principles framing, not a bounded task — route architecture questions straight to the chapter.
