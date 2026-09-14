# ADR-02: Environmental Result Architecture

## Context

The environmental results within an EPD encompass distinct categories of data: Impact Indicators (LCIA, e.g., Global Warming Potential), Resource Use (LCI, e.g., Use of renewable primary energy), Waste (LCI, e.g., Hazardous waste disposed), and Output Flows (LCI, e.g., Components for reuse). Historically, these have been bundled into a single `lciaResults` list (which is semantically incorrect since not all are LCIA) or strictly separated into multiple lists mirroring the tables found in printed EPD documents. We must decide on an architecture that prioritizes model semantics and extensibility over document structure.

## Source constraints

* Source documents (EN 15804, PCRs) enforce a strict semantic separation between Impact Indicators (LCIA) and Inventory Results (Resource Use, Waste, Output Flows).
* "MODEL SEMANTICS, NOT DOCUMENT STRUCTURES": The AAS should model the underlying data concepts, not just mirror the physical tables printed in EPD PDFs.
* Aggregating LCIA and LCI values blindly is mathematically and conceptually flawed.

## Requirements

The chosen architecture must:
* Maintain semantic correctness (never conflate LCIA with LCI).
* Minimize structural duplication in the AAS template.
* Be highly extensible to support future PCRs that might introduce new indicator types.
* Facilitate efficient querying and downstream processing.
* Utilize robust semantic IDs.

## Option A

**One Generic Results List with a Mandatory Semantic Category**

Structure: A single generic `EnvironmentalResults [SML]` containing repeatable `EnvironmentalResult [SMC]` elements. Each result has a mandatory `resultCategory` property.
Example AAS hierarchy:
```
EPD Submodel
└── EnvironmentalResults [SML]
    ├── GlobalWarmingPotential [SMC]
    │   ├── resultCategory: "ImpactIndicator" (SemanticId)
    │   └── values: ...
    ├── HazardousWaste [SMC]
    │   ├── resultCategory: "Waste" (SemanticId)
    │   └── values: ...
```

**Advantages:**
* **Extensibility:** Adding a new category (e.g., a new type of flow) doesn't require modifying the core AAS SML structure.
* **AAS Template Stability:** A single generic collection keeps the AAS template simple and prevents structural duplication of identical value matrices.
* **Model Semantics:** True to data modeling principles; the semantic `resultCategory` acts as the strict discriminator rather than relying on the structural container.

**Disadvantages:**
* Querying for *only* impact indicators requires filtering the generic list by the `resultCategory` property, rather than just extracting a pre-filtered list.

## Option B

**Separate Semantic Lists (Mirroring Document Tables)**

Structure: Separate lists for each major category defined in EN 15804.
Example AAS hierarchy:
```
EPD Submodel
├── ImpactIndicators [SML]
│   └── GlobalWarmingPotential [SMC]
├── ResourceUseIndicators [SML]
│   └── RenewableEnergy [SMC]
├── WasteIndicators [SML]
│   └── HazardousWaste [SMC]
└── OutputFlowIndicators [SML]
    └── ComponentsForReuse [SMC]
```

**Advantages:**
* Simplifies querying for downstream consumers who only want specific categories (e.g., fetching `ImpactIndicators` directly).
* Enforces separation purely by structural location.

**Disadvantages:**
* Tightly couples the AAS structure to the visual tables of current EPD documents.
* High structural duplication (the internal structure of every indicator SMC is identical, repeated across four different lists).
* Poor extensibility: if a PCR introduces a new top-level category, the AAS Submodel schema must be updated to add a new SML.

## Recommendation

**Option A** is recommended. The instruction explicitly warns: "Do NOT prefer separate result collections merely because they mirror EPD publishing tables. Remember: MODEL SEMANTICS, NOT DOCUMENT STRUCTURES." Option A offers a more robust, extensible data architecture that uses Semantic IDs (`resultCategory`) as discriminators, keeping the AAS Submodel template clean, stable, and decoupled from the layout of published PDF tables.

## Consequences

* **What becomes easier:** The AAS schema remains stable even if EPD standards introduce new classifications of indicators. Template generation is simplified.
* **What becomes harder:** Downstream consumers cannot blindly iterate a single list; they must implement a filter based on `resultCategory` if they only want to extract LCIA data.

## Programme compatibility

* **PEP ecopassport:** Fully compatible.
* **EPD International non-construction:** Fully compatible.
* **EPD International construction / EN 15804:** Fully compatible. The mandatory category ensures no semantic loss occurs when combining the lists from the original document.

## Downstream consumer perspective

Consumers will parse the `EnvironmentalResults` SML and read the `resultCategory` property for each SMC. This explicitly informs the consumer what type of data they are handling, enabling them to route it appropriately within their own LCA tools or databases.

## Breaking change impact

* **High**. Renames `lciaResults` to `EnvironmentalResults` and changes the internal structure by adding a required `resultCategory` discriminator.

## Open questions

* Should the `resultCategory` be restricted to a closed enumeration in the AAS schema, or left open for dynamic Semantic IDs mapped to an external dictionary?
