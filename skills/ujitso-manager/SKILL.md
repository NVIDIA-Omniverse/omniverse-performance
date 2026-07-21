---
name: ujitso-manager
description: UJITSO derived-data cache configuration and troubleshooting — processors, deployment models, cache locations, "first load is slow" expectations. Triggers on "UJITSO", "derived data cache", "first load slow", "scene loading cache", "cache warmup", "cache miss", "DDCS", "OmniHub".
domains:
  - omniverse
  - kit
  - caching
owner: customer-success
tags:
  - ujitso
  - kit
  - caching
  - performance
version: 1.0.0
---

# UJITSO Manager

UJITSO caches derived data (mipmapped textures, compiled shaders, optimized geometry) so subsequent loads of the same assets can skip processing. First load of a new scene is **expected** to be slower because UJITSO is populating the cache. This is the most common false-alarm partners hit.

## Processors

| Processor | Input → Output | Default | Notes |
|-----------|----------------|---------|-------|
| Textures | Source images → GPU-ready formats + mipmaps | Enabled | Biggest first-load speedup |
| Materials | MDL source → compiled shader bytecode | Enabled | Avoids runtime compilation |
| Geometry | Raw mesh → optimized, merged, deduplicated | ⚠️ Experimental / off by default | Validate on the workload |

## Key settings

| Setting | Path | Purpose |
|---------|------|---------|
| Enable | `/UJITSO/enabled` | Master toggle (default `true`) |
| Force rebuild | `/UJITSO/forceBuilds` | Force cache rebuild (default `false`) |
| Log results | `/UJITSO/logBuildResults` | Debug cache behavior |
| Verbose hash | `/UJITSO/verboseHashLogging` | Debug cache invalidation |

## Deployment models

| Model | Scope | Best for |
|-------|-------|----------|
| Local | Single user, single machine | Desktop workstations (default) |
| OmniHub | Multiple apps, same machine | Multi-app workflows |
| gRPC + DDCS | Multiple machines | Shared team caches, enterprise |

## Cache locations

- Windows: `%LOCALAPPDATA%/ov/cache/DerivedDataCache`
- Linux: `~/.cache/ov/DerivedDataCache`

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| First load slow, subsequent fast | Normal cache miss on first load | None — expected. **Tell the user this is expected behavior.** |
| "Cache exceeded" warnings | Cache over its size limit | Increase the limit or clear old entries |
| Changed assets not reflecting | Stale cache | Set `/UJITSO/forceBuilds=true` or clear the cache directory |
| Need to debug cache behavior | — | Enable `/UJITSO/logBuildResults=true` |

## Do / Don't

- ✅ **DO** explain that first-load slowness is expected. Subsequent loads use the cached data.
- ✅ **DO** check the cache directory for "Cache exceeded" warnings on long-running workstations.
- ✅ **DO** point at DDCS for shared team caches in enterprise / cloud deployments.
- ❌ **DON'T** recommend disabling UJITSO. The default is correct; first-load cost is the point.
- ⚠️ **CAUTION** with the geometry processor — experimental, off by default for a reason.

## Pre-warming for cloud / containers

For desktop workflows, running through a representative scene once is enough to warm UJITSO. For containerized deployments, cold starts pay every cache miss simultaneously — recommend a warm-up step that loads the target scene before real user traffic. See `cloud-perf-advisor` for the full pre-warming strategy.

## Source guide section

[`docs/reference/platform-systems.md`](../../docs/reference/platform-systems.md) (UJITSO section).

External reference: [UJITSO Cache System](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html), [DDCS](https://docs.nvidia.com/nvcf/overview).
