---
description: "How this guide marks Do's, Don'ts, experimental features, deprecated settings, and version notes"
---

# Conventions

Callouts in this guide use a small, consistent set of labels. Reading any chapter, the four classes of callout map onto the four most important kinds of statement:

**DO**
: A recommended action — a setting to enable, a pattern to follow, a tool to use.

**DON'T**
: A common pitfall to avoid — a setting to leave alone, an anti-pattern, or a deprecated approach.

**Experimental**
: A feature or setting that may change between Kit releases or has known trade-offs. Worth testing on your workload before shipping.

**Deprecated**
: A setting that should no longer be used. Strip it from your `.kit` files when you find it.

## Version notes

Notations such as *Kit 108+* call out behavior that depends on your Kit SDK version. If a default has changed between versions, expect to see both values listed in the configuration tables.

## Documentation links

Documentation links live next to the claim or table row they support — not in a "further reading" footer. The {doc}`/reference/sources` page collects every cited link in one indexed list, but the body of each chapter cites its own sources inline.

## Numbers in this guide

Where a recommendation is qualitative ("near-linear multi-GPU scaling at high resolution" rather than "1.8x on two GPUs"), that is deliberate. We don't publish specific numbers without a citable source, even when reviewers might expect them. The trade-off is that the guide stays defensible.

## Comments in your `.kit` file

When you change a setting in your `.kit` file or launch flags, leave a comment explaining *why* — feature, bug being worked around, or expected future fix. That comment is what lets you (or a teammate) remove the flag later when the underlying issue is resolved.
