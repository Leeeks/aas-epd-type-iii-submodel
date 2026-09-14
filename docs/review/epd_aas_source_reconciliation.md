# Source Reconciliation and Architecture Decision Backlog

This document resolves the final contradictions between the initial review, the validation pass, and the normative source texts, separating hard EPD semantics from AAS architectural choices.

## 1. Reconciling Source Facts vs Previous Conclusions

| Topic | Source facts | Previous conclusion | Corrected conclusion | Remaining architecture freedom |
|---|---|---|---|---|
| **Lifecycle Reporting Structures** | EPD Int's non-construction indicator template explicitly provides TWO reporting tabs: "alt. 1" (Upstream/Core/Downstream/Total) and "alt. 2" (A1, A2, A3... C4, D). PEP uses A1-A3, A4, A5, B, C, D. | The validation pass claimed EPD Int had abandoned Upstream/Core/Downstream for the A-D model. | The A-D model is the normative baseline for *calculations*, but "Upstream/Core/Downstream" remains a formally valid and supported *reporting aggregation* in EPD Int non-construction. | The AAS model must be capable of structurally representing BOTH reporting formats. We must choose how to represent these lifecycle stages (e.g., as a flexible vocabulary of stage identifiers). |
| **Lifecycle Modularity** | EPDs report results per lifecycle stage column. The exact columns vary by programme and PCR (e.g., A1-A3 aggregated vs A1, A2, A3 separated). | Replace booleans with `declaredModules [SML]`. | A flat list of declared modules/stages with semantic identifiers is required to support the variety of reporting columns across programs. | We must decide whether to map aggregation relationships (e.g., A1-A3 = A1+A2+A3) strictly in the AAS model or leave that to external dictionaries. |
| **Module Status Semantics** | EN 15804 / EPD Int uses "ND" (Not Declared) in result cells, and MND / MNR in boundary declarations. PEP uses exclusions/Not Applicable. | Status must be distinguishable from 0.0. | The conceptual states across all programs map to: (1) Declared (numeric), (2) Not Declared / Not Assessed, (3) Not Relevant / Not Applicable. | The AAS enum should represent the generic states. The specific source acronym (MND, MNR) can be preserved as an optional string. |
| **Content Declaration Cardinality** | EPD Int GPI (7.4.5) states: "The content declaration may not be relevant for EPDs for intangible products, such as services." | Content Declaration is a mandatory EPD core element. | Content Declaration is a fundamental Type III concept for physical goods, but cannot be strictly mandatory at the AAS schema level because EPDs for services omit it. | The `ContentDeclaration` SMC must be marked `optional` in the AAS schema, with enforcement left to the PCR-specific application rules. |
| **Functional vs Declared Unit** | PEP mandates Functional Unit but permits Declared Unit. EPD Int uses Functional Unit, but mandates Declared Unit for intermediate products where function is unknown. | Functional Unit is missing and must be added. | Both units are valid EPD concepts. Their usage is mutually exclusive or complementary depending entirely on the specific PCR. | Both `FunctionalUnit` and `DeclaredUnit` should exist as optional SMCs in the submodel, sharing a common data structure (quantity + unit). |
| **Multi-product / Family EPDs** | EPDs frequently cover a range of products using extrapolation rules or worst-case assumptions. | The AAS EPD submodel must represent the family and extrapolation factors. | The Asset Administration Shell represents a specific Asset or Asset Type. Embedding generic family extrapolation tables inside a specific Asset's shell breaks the AAS paradigm. | The EPD Submodel should provide the specific calculated results for the Asset it is attached to, while providing a reference to the Family EPD it was derived from. |
| **Result Architecture (LCI vs LCIA)** | All source documents explicitly separate Impact Indicators (LCIA) from Resource Use, Waste, and Output Flows (LCI). | Single `lciaResults` array is factually wrong. | LCI and LCIA must be separated to prevent semantic conflation and dangerous aggregation errors. | We can use separate SMC lists (`impactIndicators`, `resourceUseIndicators`, etc.) OR a single list with a strict `resultCategory` property. |
| **Semantic IDs** | `http://example.com/` and `http://eclass.example.com/` are used as placeholders. | Replace with official IDTA URIs. | We cannot mint official IDTA URIs unilaterally. | We must use a defined namespace for draft/sandbox development (e.g., `https://admin-shell.io/sandbox/idta/epd/v1/...`) until official IDs are allocated. |

---

## 2. Facts we can now treat as stable

1. **Both A-D and Upstream/Core/Downstream are valid reporting structures.** The AAS model must support exchanging data in whichever format the original EPD was published.
2. **A result value of 0.0 is semantically different from Not Declared.** A mechanism to express missing or not relevant data is mandatory.
3. **Impacts (LCIA) and Inventory Flows (LCI) are categorically distinct.** They cannot be co-mingled without a discriminator.
4. **Services do not have material content.** Therefore, Content Declaration cannot be a mandatory schema element.
5. **AAS scope vs EPD scope.** An EPD document may cover a family of products, but an AAS Submodel provides data for the specific Asset the shell describes.

---

## 3. Previous findings that should be withdrawn

*   **WITHDRAWN:** The claim that EPD International and PEP Ecopassport have incompatible, completely disjoint lifecycle models. (They use different reporting aggregations over the same underlying lifecycle phases).
*   **WITHDRAWN:** The claim that `ContentDeclaration` must be a mandatory element in the AAS schema. (It must be optional to support service EPDs).
*   **WITHDRAWN:** The assumption that the AAS EPD submodel must internally encode product-family extrapolation tables. (This violates AAS design principles; the submodel should present the resolved data for the Asset).

---

## 4. Proposed Architecture Decision Backlog

The following Architecture Decision Records (ADRs) / Open Design Decisions (ODDs) should be presented to the working group to finalise the submodel design.

### ADR-01: Representation of Lifecycle Stages and Modules
*   **Problem:** The current model hard-codes EN 15804 modules as boolean flags (`includesA1_A3`). This cannot represent individual modules (A1), alternative aggregations (Upstream/Core), or missing data statuses.
*   **Source constraints:** Must support A1-C4/D, Upstream/Core/Downstream, and explicit declaration of missing/not relevant modules.
*   **Options:**
    1. Expand the boolean list to include every possible module and aggregation.
    2. Replace booleans with a `DeclaredStages` SML, containing `Stage` SMCs with a semantic `stageCode` and `status`.
*   **Recommended option:** Option 2. It is highly extensible and maps cleanly to how EPD results are structured (as columns).
*   **Breaking-change impact:** High. Replaces the `systemBoundary` structure.
*   **Priority:** Critical.

### ADR-02: Environmental Result Categorisation
*   **Problem:** The model currently places Impact Categories (LCIA), Resource Use (LCI), and Waste (LCI) into a single `lciaResults` list. This is semantically incorrect and risks dangerous aggregations.
*   **Source constraints:** Source documents enforce strict separation of these categories.
*   **Options:**
    1. Single `environmentalResults` list with a mandatory `resultCategory` enum property on each entry.
    2. Four distinct lists: `impactIndicators`, `resourceUseIndicators`, `wasteIndicators`, `outputFlowIndicators`.
*   **Recommended option:** Option 2. It structurally enforces the semantic separation, aligns perfectly with EPD publishing tables, and simplifies querying for consumers who only want impact data.
*   **Breaking-change impact:** High. Renames and restructures the main data payload.
*   **Priority:** Critical.

### ADR-03: Representation of "Not Declared" / Null Values
*   **Problem:** `xs:decimal` cannot represent "Not Declared" (ND) or "Module Not Relevant" (MNR). A missing entry in a list is ambiguous.
*   **Source constraints:** EPDs explicitly publish "ND" or "MNR" in table cells.
*   **Options:**
    1. Use `xs:string` for all values to allow "ND". (Violates strong typing).
    2. Add a `status` enum (Declared, NotDeclared, NotRelevant) to every result cell.
    3. Define the status at the module level (ADR-01) and omit the cell if not declared. If a specific indicator is ND within a declared module, use a specific `indicatorStatus` flag.
*   **Recommended option:** Option 3. Define the macro-status at the module level, and use an optional `indicatorStatus` enum at the value level for exceptions.
*   **Breaking-change impact:** Medium.
*   **Priority:** High.

### ADR-04: Multi-Product EPDs and the Asset Administration Shell
*   **Problem:** An EPD often covers a family of products. How should this be represented in an AAS that describes a specific Asset?
*   **Source constraints:** EPD programs allow family EPDs.
*   **Options:**
    1. The submodel replicates the family extrapolation rules and all variants.
    2. The submodel provides only the calculated, specific environmental data for the current Asset, and includes an `EpdScope` metadata field indicating it was derived from a "Family Average" or "Representative" EPD, linking to the original EPD.
*   **Recommended option:** Option 2. It respects the AAS principle that a shell describes *its* asset, not a theoretical family of other assets.
*   **Breaking-change impact:** Low (additions only).
*   **Priority:** Medium.

### ADR-05: Draft Semantic Identifiers
*   **Problem:** The model uses `http://example.com` placeholders, which breaks machine resolution and violates IDTA guidelines.
*   **Source constraints:** IDTA requires valid URIs for published models.
*   **Options:**
    1. Wait for IDTA to mint official URIs.
    2. Use an explicit sandbox namespace (e.g., `https://admin-shell.io/sandbox/idta/epd/v1/...`) for the draft phase, clearly signaling they are provisional.
*   **Recommended option:** Option 2. Allows development and testing to proceed with valid URIs that won't be mistaken for final official identifiers.
*   **Breaking-change impact:** High (affects all semantic mappings).
*   **Priority:** High.
