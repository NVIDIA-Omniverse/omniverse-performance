---
description: "First-principles framing for architects: access patterns, the three-layer split (data model / runtime / wire), and what belongs in USD vs. downstream"
---

# Architecting for Performance

For architects deciding what goes where *before* there's a settings dial to turn. The rest of this guide tunes a running system; this page is about not building the wrong system in the first place.

The recurring architecture questions — *"How do we make USD fast?", "Should runtime state live in USD?", "Why is USD slow?"* — usually disappear once the system is walked from first principles. Skip that walk and every architectural question becomes a USD question.

## Performance is a first-principles question, not a USD question

In any modern computing system, performance is determined by **data access patterns relative to the memory hierarchy.** L1 hits cost a few cycles; L2 hits cost on the order of ten; DRAM misses cost hundreds. Similar hierarchies apply on GPUs (per-SM L1 / shared memory, L2 across SMs, then HBM). Branch prediction, vectorization, GC, and lock contention all matter — but they matter less than whether the data your hot loop touches is laid out for the access pattern it actually uses.

This is generic systems engineering. It is not specific to USD, scene description, robotics, or simulation. What follows for USD is straightforward:

- A **data model** — the shape of the description, how things compose, what schemas exist — is *upstream* of any specific memory layout.
- An **implementation** chooses the layout. Different implementations make different access-pattern trade-offs: Fabric's flat GPU-friendly memory; the reference C++ OpenUSD implementation; a vendor's custom binary store. All satisfy the same data model.
- Therefore **the data model itself imposes no performance cost** — cost lives in whichever implementation stores and traverses the data. The useful question is not "how do we make USD fast?" but *where to focus*: structure the content well on the data-model side, and separately choose and tune the runtime representation your deployment actually traverses. These are separate step functions — each is improved on its own terms.

## The three layers

Once performance is recognized as access-pattern-driven, the three-layer architecture below stops being a USD opinion and becomes a shape any modern simulation system converges to. Each layer's representation is dictated by its access pattern; trying to make one representation serve all three is the mistake the split exists to prevent.

| Layer | Role | Access pattern | Example representations |
|---|---|---|---|
| **Data model / interchange** | Scene description, composition, shared vocabulary, schemas | Occasional load, structured composition, no hot-loop traversal | USDA / USDC files; OpenUSD schemas |
| **Runtime** | In-memory scene representation | Hot-loop traversal, GPU-friendly, attribute-level parallel access | e.g., Fabric (see {doc}`/reference/usd-in-kit`) |
| **Inter-process / wire** | Service-to-service communication | Bandwidth-efficient encoding, low-latency RPC | gRPC; REST; message buses |

Runtime is downstream of USD: USD content is loaded or cooked into the runtime once, and the runtime owns per-frame state from there. Wire traffic is downstream of USD: nobody is shipping USDC bytes between services during simulation. **The flow is one-way, USD → runtime, with deliberate and infrequent commit-back for state the user explicitly wants to survive a save.**

## What belongs in USD, what belongs downstream

:::{admonition} DO: Author into USD what describes the initial, persistent state of the world
:class: tip

- Initial layout and asset placement
- Asset definitions — geometry, materials, kinematics, sensor configurations — and their schemas
- Composition: layering, variants, references, payloads, instancing, relocates
- Schemas as contracts between subsystems
- Persistent edits the user explicitly saves
:::

:::{admonition} DON'T: Author into USD what belongs in the runtime or on the wire
:class: warning

- Per-frame state: joint positions, simulated rigid-body transforms, particle positions, deformed meshes — these belong in the runtime layer (e.g., Fabric — see {doc}`/reference/usd-in-kit`)
- Sensor outputs: rendered frames, point clouds, pose estimates — *described* by USD schemas, *stored* in solver-native formats
- Inter-service traffic — USD is not on the wire during simulation; use gRPC / REST / message buses
- Anything in the per-frame hot loop
:::

The boundary between those two lists is the single most useful architectural call to get right early. A claim that puts something on the wrong side of the boundary is the most common shape an architecture mistake takes on this stack.

## Architecture mistakes that show up as "USD is slow"

| Phrasing | What's actually happening |
|---|---|
| "USD is slow" | Almost always extension overhead, traversal patterns, or runtime miscoding. Rarely USD itself — and never the data model. See {doc}`/reference/usd-in-kit` for the USDRT/Fabric fix. |
| "How do we make USD fast?" | Split the question — data model and runtime are separate step functions. Content structure (composition, instancing, payloads) is one lever; per-frame speed comes from the runtime representation (see {doc}`/reference/usd-in-kit`). Where code does touch the stage directly, the cost is in the access path chosen, not in the data model. |
| "USD lacks dynamic scene creation" | Scope confusion. Dynamic mutation is a runtime concern; USD describes the initial state. Mutate in Fabric. |
| "Should we author runtime physics state into USD?" | Almost never. Runtime state lives downstream. USD captures persistent edits the user explicitly saves. |
| "We need USD to support [solver-internal feature]" | Almost never. The solver runs in its own optimized representation; USD schemas describe its inputs and outputs, not its internals. |

If a question conflates layers, surface the conflation before answering. The conversation that follows is the one that produces aligned decisions.

:::{seealso}
- {doc}`/get-started/quick-start` — Once the architecture is right, the five-minute settings checklist
- {doc}`/reference/usd-in-kit` — USDRT and Fabric: the runtime side of the layer split, with runnable code
- {doc}`/reference/usd-scene-structure` — Authoring decisions inside the USD layer (payloads, layers, instancing)
- {doc}`/reference/platform-systems` — FSD, UJITSO, and the cache landscape between data model and runtime
:::
