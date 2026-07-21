---
description: "UJITSO derived-data cache reference for the AI skill tree — processors, deployment models, troubleshooting"
---

# UJITSO Configuration Reference

Source: [UJITSO Cache System](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html).

## Processors

| Processor | Default | Notes |
|-----------|---------|-------|
| Textures | Enabled | Major first-load speedup |
| Materials | Enabled | Avoids runtime shader compilation |
| Geometry | Disabled | Experimental — validate on your workload |

## Key settings

| Setting | Path | Purpose |
|---------|------|---------|
| Enable | `/UJITSO/enabled` | Master toggle (default: `true`) |
| Force rebuild | `/UJITSO/forceBuilds` | Force cache rebuild (default: `false`) |
| Log results | `/UJITSO/logBuildResults` | Debug cache behavior |
| Verbose hash | `/UJITSO/verboseHashLogging` | Debug cache invalidation |

## Deployment models

| Model | Scope | Best for |
|-------|-------|----------|
| Local | Single user / machine | Desktop (default, zero config) |
| OmniHub | Multiple apps, same machine | Multi-app workflows |
| gRPC + DDCS | Enterprise, multi-machine | Shared team caches ([DDCS docs](https://docs.nvidia.com/nvcf/overview)) |

## Cache locations

- Windows: `%LOCALAPPDATA%/ov/cache/DerivedDataCache`
- Linux: `~/.cache/ov/DerivedDataCache`

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| First load slow, subsequent fast | Normal — cache miss |
| "Cache exceeded" | Increase the limit or clear old entries |
| Changed assets not reflecting | `/UJITSO/forceBuilds=true` or clear the cache directory |
| Need to debug cache behavior | Enable `/UJITSO/logBuildResults=true` |
