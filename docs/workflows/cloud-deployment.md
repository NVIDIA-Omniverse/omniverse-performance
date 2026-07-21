---
description: "USD-on-cloud-storage trade-offs, access patterns, caching architecture, pre-warming, and bandwidth for Omniverse deployments"
---

# Cloud Deployment

Cloud introduces a different set of performance challenges than desktop. Missing caches, network latency between compute and storage, and cold container starts all compound. Partners typically hit these later in their pipeline — local development works fine, then they deploy and everything is slow.

## Quick reference — Do's and Don'ts

:::{admonition} DO: Develop and profile locally first
:class: tip

You should be able to exercise and profile the end-to-end application outside of production. This catches performance issues early, without needing to figure out cloud profiling.
:::

:::{admonition} DO: Deploy applications in the same availability zone as your USD content
:class: tip

Network latency between compute and storage can dominate; differing availability zones is a common cause.
:::

:::{admonition} DO: Match asset structure to your access pattern
:class: tip

Interactive exploration wants payload-based assets so the client controls what gets fetched; batch processing wants flattened or consolidated USD so each job pays a single fetch. See [Application access patterns](#application-access-patterns) below and {doc}`/reference/usd-scene-structure` for the authoring side.
:::

:::{admonition} DO: Pre-warm caches before production traffic
:class: tip

UJITSO, shader cache, and USD content caches all need warming. First-load penalties are severe in cloud — see [Pre-Warming Strategy](#pre-warming-strategy) below.
:::

:::{admonition} DO: Use cloud object storage with multipart upload/download
:class: tip

Enables parallel transfers for large USD files.
:::

:::{admonition} DO: Minimize Kit application container size
:class: tip

Faster application startup. Leverage in-cluster container image caches if available.
:::

:::{admonition} DON'T: Assume local development performance translates to cloud
:class: warning

Missing caches, network latency, and containerization overhead can have a big impact.
:::

:::{admonition} DON'T: Skip cache configuration for cloud deployments
:class: warning

Every cache type needs explicit configuration in cloud — none "just work" the way they do locally.
:::

:::{admonition} DON'T: Rely on directory layout for fetch performance
:class: warning

Object stores fan storage across distributed nodes; "directories" and prefixes are organizational, not physical-locality hints. Listing a prefix queries a distributed index, and "nearby" files aren't faster to fetch together. If you need related assets fetched together, bundle them or list them up front in a manifest layer.
:::

## How USD reads from cloud storage

USD doesn't stream files. Each referenced file goes through download → parse → compose before any prim under it is traversable. On a fast local disk this is cheap; over a network it adds friction at every link in the reference chain. Three properties of cloud object storage shape the rest of this chapter:

- **Per-request latency dominates small fetches.** A reference chain of `A → B → C` becomes a serial waterfall — each round-trip blocks the next. Shallow hierarchies and parallel-fetchable manifests help; deep chains do not.
- **There is no index.** USD files have no internal byte-range structure you can query. The client downloads the whole file, then parses it. Selective attribute fetching is application-level work, not a storage-layer query — see [Maximizing USD Performance](https://openusd.org/release/maxperf.html).
- **Prefixes are not locality.** Object stores spread data across nodes for durability; directory structure is organizational. Treat USD files as opaque blobs from the storage layer's perspective.

The practical consequence is a structural trade-off:

| Asset structure | What it costs you on cloud | What it gives you |
|-----------------|----------------------------|-------------------|
| Many small files (payload-based) | More round-trips; reference chains create waterfalls | Load only what's needed, fast initial open, fine cache granularity |
| Consolidated bundles (e.g. `.usdz`) | Larger fetch even if you only need a slice; full re-download on any change | One round-trip gets everything; predictable load time |

Neither is universally better. Match the structure to your access pattern (next section) and let payload arcs push the load/no-load decision out to the client. Authoring details for payloads, layers, and bundles live in {doc}`/reference/usd-scene-structure`.

## Application access patterns

Different workloads want different asset structure and cache strategy. The three patterns below cover most partner deployments.

### Interactive exploration

A user navigates a large scene, drilling into assets on demand.

- **Friction:** deep reference chains turn each interaction into a waterfall request, and each hop adds round-trip latency.
- **Authoring:** keep reference hierarchies shallow. Use payload arcs for heavy geometry so the client decides when to load — see {doc}`/reference/usd-scene-structure`.
- **Runtime:** speculatively prefetch based on camera frustum or user navigation. A "manifest" layer that declares all transitive dependencies up front lets the client fan out fetches in parallel rather than discovering them one hop at a time.

### Batch processing

A render farm or simulation cluster processes whole scenes; many workers hit the same assets simultaneously.

- **Friction:** thousands of cold caches at once; network is the bottleneck.
- **Authoring:** publish flattened or consolidated USD for batch consumption — pay the flattening cost once at publish time. File caching alone doesn't eliminate USD composition cost (resolving references, evaluating LIVRPS, applying variants); flattening at publish time removes that work from the per-job hot path. USDZ bundles that include all dependencies are the case where the {doc}`/reference/usd-scene-structure` chapter's USDZ DON'T does not apply.
- **Runtime:** warm assets ahead of job dispatch; deploy a regional or in-cluster cache (UCC, CDN, NVIDIA Storage APIs) so workers hit a local replica instead of the origin.

### Real-time collaboration

Multiple users edit the same scene simultaneously.

- **Friction:** write contention on shared layers, stale reads without explicit invalidation, and merge happens at the layer level rather than the prim level.
- **What works:** session-scoped layers that merge at save time; optimistic locking with versioning. None of this is provided by vanilla cloud storage.
- **What's purpose-built:** [NVIDIA Omniverse Nucleus](https://docs.omniverse.nvidia.com/nucleus/latest/index.html) is the supported collaborative-USD infrastructure. For partners building on cloud object storage directly, real-time multi-user editing is genuinely hard and worth scoping carefully.

## Cloud caching architecture

```{mermaid}
flowchart TD
    subgraph shaders["RTX shader compilation"]
        gx["GXCache (NVCF)"]
        okas["OKAS Memcached<br/>(Kit App Streaming)"]
        local["Local filesystem<br/>(no config needed)"]
    end
    subgraph derived["Derived runtime artifacts (UJITSO)"]
        umat["Materials → compiled<br/>shader bytecode"]
        utex["Textures → GPU-ready<br/>formats + mipmaps"]
        ugeo["Geometry → optimized mesh<br/>experimental"]
    end
    subgraph content["USD content cache"]
        clib["Omniverse Client Library<br/>(local FS cache)"]
        ucc["USD Content Cache (UCC)<br/>(NVCF)"]
        cdn["CDN / NVIDIA Storage APIs<br/>caching layer"]
    end
```

A vetted, NVIDIA-styled diagram of this architecture is a follow-up; this Mermaid version shows the relationships. The canonical reference for cloud-deployment caches is [Simulation Cluster Caches — NVIDIA Cloud Functions](https://docs.nvidia.com/nvcf/overview).

## Cache types & configuration

| Cache | Purpose | Cloud deployment | Docs |
|-------|---------|-----------------|------|
| **RTX Shader Cache** | Pre-compiled shaders | GXCache (NVCF) or Memcached (OKAS) | [GXCache](https://docs.nvidia.com/nvcf/overview), [OKAS Memcached](https://docs.omniverse.nvidia.com/ovas/latest/deployments/infra/installation.html#install-memcached-service) |
| **UJITSO Cache** | Derived data (textures, materials, geometry) | gRPC + DDCS for shared team caches | [UJITSO](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/ujitso.html), [DDCS](https://docs.nvidia.com/nvcf/overview) |
| **USD Content Cache** | USD files and referenced assets | Omniverse Client Library + UCC | [Client Library](https://docs.omniverse.nvidia.com/kit/docs/client_library/latest/index.html), [UCC](https://docs.nvidia.com/nvcf/overview) |
| **Shared Shader Cache** | Pre-compiled shaders for Kit App Streaming | Memcached service | [Shared Shader Cache](https://docs.omniverse.nvidia.com/ovas/latest/architecture/shader-cache.html) |

Each cache has different ownership and different configuration patterns. There is no unified cache management interface — pre-warming is per-cache (see below).

## Pre-Warming Strategy

A cold container start hits every cache miss simultaneously: no compiled shaders, no UJITSO cache, no local USD files. This can turn a five-second warm load into a multi-minute cold load. A pre-warming step is not optional for production cloud deployments.

| Cache | Warm-up trigger | How to pre-warm |
|-------|-----------------|-----------------|
| **UJITSO** | First scene load processes and caches derived data | Load the scene once in a warm-up step before production |
| **RTX Shader** | First render compiles shaders | Render the scene once; use GXCache/Memcached to share across instances |
| **USD Content** | First file access downloads and caches | Pre-fetch assets via Omniverse Client Library; use UCC in NVCF |

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

## Storage and bandwidth

- Use cloud object storage (S3, GCS, Azure Blob) with multipart upload/download.
- Download diffs/changes to existing content where possible; use compression.
- Use a CDN in front of origin storage, or [NVIDIA Omniverse Storage APIs](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/collections/storage_apis) as a file-caching layer.
- Deploy compute in proximity to content — same availability zone or region.

Cloud egress costs add up at scale. Every cache hit is bytes you didn't pay egress for, which is part of why the cache layers above are worth investing in early. Surface egress as a deployment-level metric alongside latency and FPS so you notice when a workload starts hammering the origin instead of the regional or in-cluster cache.

## Profiling in containerized environments

Tracy can be configured for remote capture from containerized environments — useful when you need to profile against the production environment rather than a local repro. See the [Tracy profiler extension docs](https://docs.omniverse.nvidia.com/extensions/latest/ext_profiler_tracy.html) for the remote-capture setup.

For load-time issues observed only in cloud, the {doc}`/get-started/profiling` activity timeline usually points clearly at materials/textures (UJITSO not warmed) or network/file fetch (UCC, Client Library, or origin storage) — those are the two things that cold-start cloud breaks first.
