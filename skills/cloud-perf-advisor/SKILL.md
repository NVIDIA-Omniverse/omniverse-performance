---
name: cloud-perf-advisor
description: Cloud deployment performance — caching architecture, pre-warming strategy, container cold starts, NVCF, OKAS, UCC, GXCache, DDCS. Triggers on "cloud performance", "container startup", "K8s profiling", "cloud caching", "cold start", "NVCF", "GXCache", "OKAS", "UCC", "deployment performance", "Kit App Streaming".
domains:
  - omniverse
  - cloud
owner: customer-success
tags:
  - cloud
  - kit
  - caching
  - nvcf
  - okas
  - performance
version: 1.0.0
---

# Cloud Performance Advisor

Cloud introduces a different set of performance challenges than desktop. Missing caches, network latency between compute and storage, and cold container starts compound. Partners typically hit these later in their pipeline — local development works fine, then they deploy and everything is slow.

## The pre-warming reality

A cold container start hits every cache miss simultaneously: no compiled shaders, no UJITSO cache, no local USD files. This can turn a five-second warm load into a multi-minute cold load. **A pre-warming step is not optional for production cloud deployments.**

## Caches partners need to think about

Each cache has different ownership and different configuration patterns. There is no unified cache management interface — pre-warming is per-cache.

| Cache | Purpose | Cloud deployment | Docs |
|-------|---------|------------------|------|
| RTX Shader Cache | Pre-compiled shaders | GXCache (NVCF) or Memcached (OKAS) | [GXCache](https://docs.nvidia.com/nvcf/overview), [OKAS Memcached](https://docs.omniverse.nvidia.com/ovas/latest/deployments/infra/installation.html#install-memcached-service) |
| UJITSO Cache | Derived data (textures, materials, geometry) | gRPC + DDCS for shared team caches | [UJITSO](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html), [DDCS](https://docs.nvidia.com/nvcf/overview) |
| USD Content Cache | USD files and referenced assets | Omniverse Client Library + UCC | [Client Library](https://docs.omniverse.nvidia.com/kit/docs/client_library/latest/index.html), [UCC](https://docs.nvidia.com/nvcf/overview) |
| Shared Shader Cache | Pre-compiled shaders for Kit App Streaming | Memcached service | [Shared Shader Cache](https://docs.omniverse.nvidia.com/ovas/latest/architecture/shader-cache.html) |

## Pre-warming strategy

| Cache | Warm-up trigger | How to pre-warm |
|-------|-----------------|-----------------|
| UJITSO | First scene load processes and caches derived data | Load the scene once in a warm-up step before production |
| RTX Shader | First render compiles shaders | Render the scene once; use GXCache/Memcached to share across instances |
| USD Content | First file access downloads and caches | Pre-fetch assets via Omniverse Client Library; use UCC in NVCF |

In practice this is an init container or startup script:

```
1. Startup script
   ├── Download USD content                → warms Client Library cache
   ├── Load target scene with Kit (headless) → warms UJITSO cache
   ├── Render one frame                     → warms shader cache
   └── (Optional) persist cache volumes across container restarts

2. Shared cache infrastructure
   ├── GXCache (NVCF) or Memcached (OKAS)  → share shaders across pods
   ├── UJITSO gRPC + DDCS                  → share derived data across team
   └── UCC                                 → share USD content across NVCF

3. Cache volume management
   ├── Mount persistent volumes for UJITSO cache directory
   ├── Mount persistent volumes for shader cache directory
   └── Configure cache size limits to prevent disk pressure
```

## Do / Don't

- ✅ **DO** develop and profile locally first. Be able to exercise and profile the end-to-end application outside production.
- ✅ **DO** deploy applications in the same availability zone as your USD content. Network latency between compute and storage can dominate.
- ✅ **DO** pre-warm caches before production traffic.
- ✅ **DO** use cloud object storage with multipart upload/download for large USD files.
- ✅ **DO** minimize Kit application container size — faster startup. Leverage in-cluster container image caches when available.
- ✅ **DO** condition content in a separate, Kit-free build step where you can. The Asset Validator (`pip install usd-validation-nvidia`) and Scene Optimizer ([`usd-optimize`](https://github.com/NVIDIA-Omniverse/usd-optimize)) both run standalone, so a CI / preprocessing stage can validate and optimize USD in a lean container instead of inside the full Kit runtime.
- ❌ **DON'T** assume local performance translates to cloud. Missing caches, network latency, and containerization overhead can have a big impact.
- ❌ **DON'T** skip cache configuration for cloud. None of the caches "just work" the way they do locally.

## Profiling in containerized environments

Tracy can be configured for remote capture from containerized environments — useful when profiling against production rather than a local repro. See the [Tracy profiler extension docs](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler_tracy.html).

For load-time issues observed only in cloud, the activity timeline (route to `profiling-guide`) usually points clearly at:

- Materials/textures dominating → UJITSO cache not warmed.
- Network/file fetch dominating → UCC, Client Library, or origin storage cold.

Those are the two things cold-start cloud breaks first.

## Storage best practices

- Use cloud object storage (S3, GCS, Azure Blob) with multipart upload/download.
- Download diffs/changes to existing content where possible; use compression.
- Use a CDN in front of storage, or NVIDIA Storage APIs as a file-caching layer.
- Deploy in proximity to content — same availability zone or region.

## Source guide section

[`docs/workflows/cloud-deployment.md`](../../docs/workflows/cloud-deployment.md).

External references: [Simulation Cluster Caches](https://docs.nvidia.com/nvcf/overview), [GXCache](https://docs.nvidia.com/nvcf/overview), [DDCS](https://docs.nvidia.com/nvcf/overview), [UCC](https://docs.nvidia.com/nvcf/overview), [Omniverse Client Library](https://docs.omniverse.nvidia.com/kit/docs/client_library/latest/index.html).
