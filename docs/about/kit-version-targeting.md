---
description: "Why this guide targets Kit 109/110 and what changes when you move between Kit versions"
---

# Kit Version Targeting

Examples and defaults in this guide assume **Kit 109 or 110**. Older releases (107 and earlier) are end-of-life or near it; if you are on an older branch, expect some defaults and behaviors to differ.

**Currency.** Version-specific defaults here were last verified against **Kit 110.0.0**. Where a default is noted as in flux, confirm it against the linked configuration docs for your exact Kit version rather than trusting a fixed value here.

The single most useful first step when investigating any performance issue is to **reproduce against the latest Kit and a stock app template**. Many issues are already fixed upstream; the problem is in customizations layered on an older Kit branch, not in Kit itself.

## Reproduce against the stock template

Disable custom extensions and run the workload in the unmodified Kit App Editor template. If the issue does not reproduce, the problem is in your app's customizations, not Kit.

[Kit App Template repo](https://github.com/NVIDIA-Omniverse/kit-app-template).

## Defaults that have flipped

| Setting | Path | Older default | Current default | Note |
|---------|------|--------------|-----------------|------|
| FSD master switch | `/app/useFabricSceneDelegate` | `false` (pre-Kit 109) | `true` (Kit 109+) | See {doc}`/reference/platform-systems` |
| Merge materials | `/app/usdrt/population/utils/mergeMaterials` | `true` | `false` (Kit 108+) | Off by default since Kit 108; opt-in optimization, incompatible with NeurayLib materials. See {doc}`/reference/platform-systems` |
| Instance compact transforms | `/app/usdrt/population/utils/instanceCompactTransforms` | enabled in some templates | deprecated since Kit 108.0 | Strip from `.kit` files |

## Memory improvements ride on the upgrade

Some platform improvements are not knobs — they are gained automatically by updating Kit. The most concrete recent example is zero-copy `VtArray` sharing between USD and Fabric, available from Kit 109 onward, which reduces system memory for the same scene without any configuration. There is no "verify" setting; updating is the lever.

:::{seealso}
- {doc}`/reference/platform-systems` — full FSD configuration reference
- {doc}`/workflows/troubleshooting` — Scenario 6 (regression after Kit upgrade)
:::
