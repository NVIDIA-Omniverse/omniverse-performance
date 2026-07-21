---
description: "Troubleshooting scenarios reference for the AI skill tree — symptoms, root causes, resolution paths"
---

# Troubleshooting Scenarios Reference

Structured summary of the scenarios documented in {doc}`/workflows/troubleshooting`. Each scenario lists the symptom, common root causes, and the resolution path to follow.

## First three checks (apply to every scenario)

1. Reproduce against the latest Kit (Kit 109 or 110). Many issues are already fixed upstream.
2. Reproduce against a stock Kit App Editor template with custom extensions disabled. If it doesn't reproduce, the issue is in the customizations, not Kit.
3. Check the GPU driver against [Technical Requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html). A wrong/unsupported driver is one of the most common single root causes for crashes and unexpected performance.

---

## Scenario 1: Slow scene loading

**Common root causes**: `.usda` format on heavy data, layer counts grown procedurally, no payloads, network latency to content, missing/cold UJITSO cache.
**Resolution path**: format → layers → payloads → cache → network → activity-timeline-driven incremental loading.

## Scenario 2: Single-digit FPS during navigation

**Common root causes**: GPU-bound (complex materials, extreme bounds, glass bounce-count compound), CPU-bound (prim count, Python traversal, `TfNotice`), memory-bound.
**Resolution path**: profiler trace → identify bound → Scene Optimizer (memory or FPS path) → DLSS Super Resolution → bounce-count tuning. Consider geometry streaming only as an experiment when GPU memory is the bottleneck.

## Scenario 3: GPU crashes / device-lost

**Common root causes**: Wrong/unsupported driver (most common), stale UJITSO cache, texture VRAM exceeded, malformed USD, Kit bugs already fixed in newer versions.
**Resolution path**: driver check first → clear UJITSO cache → check texture-streaming budget → reduce viewports → check USD validity → update Kit.

## Scenario 4: Instanced scene still uses too much memory

**Common root causes**: `instanceable=true` not set, or set on hierarchies that are not actually referenced/payloaded multiple times to the same source; `enableRendererInstancing` off; `mergeMaterials` off (off by default since Kit 108).
**Resolution path**: verify `instanceable=true` is on a *referenced/payloaded* prim → confirm asset is actually referenced multiple times to the same source → enable `enableRendererInstancing` (experimental, RTX-only) → enable `mergeMaterials` (off by default since Kit 108; NeurayLib caveat) → confirm Kit 109+ for zero-copy VtArray sharing → consider point instancing for very high counts.

## Scenario 5: Scene looks wrong after optimization

**Common root causes**: Normals flipped by merge/decimation, material bindings changed by dedup, mesh integrity broken.
**Resolution path**: Generate Normals → check material assignments → Weld Checker → review optimizer report → re-run with adjusted parameters.

## Scenario 6: Performance regression after Kit upgrade

**Common root causes**: Default settings flipped between Kit versions (notably `useFabricSceneDelegate` to `true` in 109; `mergeMaterials` off by default since 108; `instanceCompactTransforms` deprecated since 108); branched app diverged from the current template.
**Resolution path**: read migration / release notes → compare `.kit` against the current Kit App Template → verify FSD enabled → verify `mergeMaterials` setting matches your content type → strip deprecated settings → reproduce on stock template.
