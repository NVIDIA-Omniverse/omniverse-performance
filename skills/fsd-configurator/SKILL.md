---
name: fsd-configurator
description: Fabric Scene Delegate (FSD) configuration — the small set of settings partners actually need to consider, with the mergeMaterials default (off by default since Kit 108) context and the deprecated instanceCompactTransforms warning. Triggers on "FSD", "Fabric Scene Delegate", "Fabric", "mergeMaterials", "enableRendererInstancing", "populateAllAuthoredAttributes", "useFabricSceneDelegate", "instanceCompactTransforms".
domains:
  - omniverse
  - kit
owner: customer-success
tags:
  - fsd
  - fabric
  - kit
  - performance
  - usdrt
version: 1.0.0
---

# FSD Configurator

The Fabric Scene Delegate (FSD) is the modern rendering pipeline. Most performance questions touch FSD configuration in some way.

## The default-first principle

Recommend that users **keep defaults unless they have a specific reason to change them**. When a setting must be changed, recommend leaving a comment in the `.kit` file explaining *why* — feature, bug being worked around, or expected future fix. That comment is what lets the flag be removed later when the underlying issue is resolved.

The settings table below is intentionally narrow — it surfaces only the flags partners actually need to consider. Most other FSD-population flags should stay at their defaults.

## Configuration reference

| Setting | Path | Default (Kit 109+) | Recommendation | Status |
|---------|------|--------------------|----------------|--------|
| Enable FSD | `/app/useFabricSceneDelegate` | `true` (Kit 109+), `false` earlier | Always on | — |
| Merge materials | `/app/usdrt/population/utils/mergeMaterials` | `false` (Kit 108+), `true` earlier | Opt-in optimization — enable for static stages with many duplicate materials, not using NeurayLib materials | Off by default since Kit 108 |
| Renderer-side instancing | `/app/usdrt/population/utils/enableRendererInstancing` | `false` | Test on heavily-instanced scenes | ⚠️ Experimental, RTX renderer only |
| Populate all authored attributes | `/app/usdrt/population/utils/populateAllAuthoredAttributes` | `false` | Off for rendering. Enable only when you specifically need custom attrs in Fabric — costs memory | — |
| Instance compact transforms | `/app/usdrt/population/utils/instanceCompactTransforms` | n/a | **Do not use** | 🗑️ Deprecated since Kit 108.0 |

## The `mergeMaterials` default (most common partner question)

`mergeMaterials` has been off by default since Kit 108 (it was `true` in earlier versions) — that's the stable default, not a temporary flip. It deduplicates identical materials to save memory, but it is incompatible with NeurayLib materials and affected variant/material-swapping content (notably automotive configurators), which is why it ships off. Treat it as an opt-in optimization.

- Static stages with many duplicate materials and **no** NeurayLib materials should turn `mergeMaterials` **on** — such stages can load noticeably faster with it enabled.
- Content using NeurayLib materials or variant/material swapping should leave it **off**.

## The `instanceCompactTransforms` story (frequently misunderstood)

This setting is **deprecated since Kit 108.0**. Older guides and templates that recommended setting `instanceCompactTransforms=1` are stale. Strip it from `.kit` files when you find it. It is mutually exclusive with `useMatrixForInstanceProxyTransforms`, which is the recommended path now.

**Do not list it as a recommended memory-optimization flag.**

## Launch-flag block (when needed)

```bash
# FSD master switch
--/app/useFabricSceneDelegate=1

# Opt-in optimization: mergeMaterials is off by default (Kit 108+).
# Reason: static stage with many duplicate materials, no NeurayLib materials.
--/app/usdrt/population/utils/mergeMaterials=1

# EXPERIMENTAL: validate before shipping. RTX renderer only.
--/app/usdrt/population/utils/enableRendererInstancing=1
```

Always include the `# Reason:` comment when generating launch-flag blocks for users — that's the convention for this guide.

## Do / Don't

- ✅ **DO** verify FSD is enabled on existing apps. Older Kit App Template branches may have it explicitly disabled by workarounds.
- ✅ **DO** quote full setting paths verbatim (`/app/usdrt/population/utils/mergeMaterials`, never just `mergeMaterials`).
- ✅ **DO** leave a comment in the `.kit` file when changing any FSD setting.
- ❌ **DON'T** disable FSD unless there's a specific, documented reason. The OmniHydra fallback path is legacy.
- 🗑️ **DON'T** recommend `instanceCompactTransforms=1`. Deprecated since Kit 108.0.
- ⚠️ **CAUTION** when recommending `enableRendererInstancing` — experimental and RTX renderer only.

## Source guide section

[`docs/reference/platform-systems.md`](../../docs/reference/platform-systems.md).

External reference: [FSD Configuration & Settings](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html).
