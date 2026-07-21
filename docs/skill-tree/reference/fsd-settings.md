---
description: "FSD configuration reference for the AI skill tree — settings, defaults, and Kit version notes"
---

# FSD Configuration Reference

Source: [FSD Configuration](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/latest/fabricsd/configuration.html). Defaults assume Kit 109 / 110.

This reference is intentionally narrow — it surfaces only the FSD population settings partners actually need to consider. For the complete FSD configuration surface, link out to the canonical doc rather than duplicating it here.

| Setting | Path | Default (Kit 109+) | Recommendation | Status |
|---------|------|--------------------|----------------|--------|
| Enable FSD | `/app/useFabricSceneDelegate` | `true` | Always on | — |
| Merge materials | `/app/usdrt/population/utils/mergeMaterials` | `false` (was `true` pre-108) | Opt-in optimization — enable for static stages with many duplicate materials, not using NeurayLib materials | Off by default since Kit 108 |
| Renderer-side instancing | `/app/usdrt/population/utils/enableRendererInstancing` | `false` | Test on heavily-instanced scenes; validate before shipping | Experimental, RTX renderer only |
| Populate all authored attributes | `/app/usdrt/population/utils/populateAllAuthoredAttributes` | `false` | Off for rendering. Enable only when you specifically need custom authored USD attributes accessible from Fabric — costs memory | — |
| Instance compact transforms | `/app/usdrt/population/utils/instanceCompactTransforms` | n/a | Do not use | Deprecated since Kit 108.0 |

## Launch flag block — large instanced stage

```bash
# FSD master switch
--/app/useFabricSceneDelegate=1

# Opt-in optimization: mergeMaterials is off by default (Kit 108+).
# Reason: static stage with many duplicate materials, no NeurayLib materials.
--/app/usdrt/population/utils/mergeMaterials=1

# EXPERIMENTAL: validate before shipping. RTX renderer only.
--/app/usdrt/population/utils/enableRendererInstancing=1
```

When you change a setting in your `.kit` file or launch flags, leave a comment explaining *why* — feature, bug being worked around, or expected future fix. That comment is what lets the flag be removed later when the underlying issue is resolved.
