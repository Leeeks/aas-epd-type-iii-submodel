# ADR-01: Lifecycle Representation

## Context

The model must support different lifecycle reporting structures. Environmental Product Declarations (EPDs) publish their results according to varying lifecycle stage aggregations depending on the specific program and Product Category Rules (PCR). Examples include reporting by individual stages (A1, A2, A3), aggregated stages (A1-A3), other specific phases (A4, A5, B1-B7, C1-C4, D), or completely different categorical aggregations like Upstream, Core, Downstream, and Total. The challenge is representing these variations flexibly without hardcoding them into the schema as flat strings or a rigidly closed enumeration. We must accurately capture the lifecycle stage identity, the specific reporting scheme, the declaration status, and complex aggregation relationships.

## Source constraints

* Programs like PEP Ecopassport commonly use lifecycle structures such as A1-A3, A4, A5, B, C, D.
* EPD International for non-construction products supports structures like Upstream/Core/Downstream/Total as well as A1-C4/D depending on the specific reporting tab.
* Lifecycle designations (e.g., `A1-A3`) are not merely arbitrary flat strings; they have semantic meaning and can be decomposed or related to other stages (e.g., `A1`, `A2`, `A3`).
* The source data often explicitly separates the reporting structure from the underlying lifecycle calculation model.

## Requirements

The chosen architecture must be able to:
* Support any lifecycle reporting structure (A1-A3, Upstream, etc.) using repeatable declarations.
* Use semantic references to define the identity of the lifecycle stage.
* Distinguish between the stage identity, the overarching lifecycle reporting scheme, the declaration/status of the stage, and any aggregation relationships.
* Prevent the model from being restricted by a permanently closed enumeration.

## Option A

**Hardcoded SubmodelElementCollections per Lifecycle Stage**

Structure: A rigidly defined set of optional boolean flags or sub-collections for every known stage and common aggregation.
Example AAS hierarchy:
```
EPD Submodel
└── LifecycleStages [SML]
    ├── A1 [SMC] (Status: Declared)
    ├── A2 [SMC] (Status: Declared)
    └── A1_A3 [SMC] (Status: Declared)
```

**Advantages:**
* Simple to validate against a strictly known schema.
* Easy to query if the exact needed stage is directly implemented.

**Disadvantages:**
* Cannot scale to accommodate new reporting schemes or PCR-specific aggregations (e.g., A1-A2, or Upstream).
* Forces the standard to frequently update the schema when new phases or aggregations are introduced.
* Fails to explicitly map the mathematical/aggregation relationships between A1, A2, A3 and A1-A3.

## Option B

**Generic Repeatable Stages with Semantic Identifiers and Aggregation Links**

Structure: A generic `DeclaredStages` list where each entry defines a stage using a semantic ID, its reporting scheme, and optional aggregation relationships.
Example AAS hierarchy:
```
EPD Submodel
└── LifecycleReportingScheme (ConceptDescription / SemanticId)
└── DeclaredStages [SML]
    ├── Stage [SMC]
    │   ├── StageId: "A1-A3" (SemanticId)
    │   ├── Status: "Declared"
    │   └── Aggregates: ["A1", "A2", "A3"] (List of SemanticIds)
    └── Stage [SMC]
        ├── StageId: "A4" (SemanticId)
        └── Status: "Declared"
```

**Advantages:**
* Fully extensible; supports any reporting structure (Upstream, A1-A3, custom PCR phases) without schema changes.
* Distinct separation between identity, scheme, and status.
* Aggregation relationships make it explicitly clear when a stage represents a sum of other stages, avoiding double-counting errors.

**Disadvantages:**
* Slightly higher complexity for downstream consumers to interpret, as they must resolve semantic IDs rather than relying on hardcoded property names.

## Recommendation

**Option B** is recommended. It prevents the model from relying on a closed enumeration or flat strings, and aligns with the requirement to semantically reference lifecycle stages. It explicitly allows the model to state that "A1-A3" is an aggregation of A1, A2, and A3, providing the extensibility needed across various EPD programs (EPD International, PEP, etc.).

## Consequences

* **What becomes easier:** Adding support for new PCRs or alternative reporting structures (like Upstream/Core/Downstream) requires zero changes to the AAS schema.
* **What becomes harder:** Downstream consumers cannot simply look for a property named `A1`. They must iterate through the `DeclaredStages` and check the semantic `StageId`.

## Programme compatibility

* **PEP ecopassport:** Fully compatible. Can map their specific aggregated stages (e.g., A1-A3, B, C) using appropriate semantic IDs.
* **EPD International non-construction:** Fully compatible. Allows reporting using Upstream/Core/Downstream semantics.
* **EPD International construction / EN 15804:** Fully compatible. Maps directly to the A1-C4/D module framework.

## Downstream consumer perspective

A consumer receiving the AAS would parse the `DeclaredStages` list. They would look at the `StageId` semantic reference to understand what phase is being reported. If they encounter an unknown stage, they can inspect the `Aggregates` field to see if it decomposes into known stages, or rely on the `LifecycleReportingScheme` for context, safely ignoring phases they do not process without breaking their software.

## Breaking change impact

* **High**. This completely replaces any existing hardcoded boolean module flags or rigid lifecycle structures with a generic SML structure. Affected elements: `systemBoundary`, `includesA1_A3`, etc.

## Open questions

* Should the aggregation relationships (e.g., A1-A3 = A1 + A2 + A3) be strictly defined within the AAS instance payload, or should the AAS instance just provide the Semantic ID for "A1-A3" and leave the decomposition logic to an external dictionary?
