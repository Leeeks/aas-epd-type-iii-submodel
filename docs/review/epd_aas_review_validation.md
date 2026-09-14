# Validation of the Adversarial Architectural Review: AAS EPD Type III Submodel

This document validates the findings of the initial adversarial review against the normative source documents (PEP Ecopassport PCR Ed.4 and EPD International GPI 5.0.1 / EN 15804+A2). It serves as a defensible basis for IDTA working group decisions.

## 1. Validation of Findings (Blocker and High Severity)

| Original finding | Validation status | Evidence | Corrected interpretation | Recommended next action |
|---|---|---|---|---|
| **PEP/EPD Int lifecycle structure (Upstream/Core/Downstream)** vs `systemBoundary` booleans | REVISE | PEP PCR Ed.4 (Fig 3 & 4, pp. 58-59) explicitly maps stages to EN 15804 A1-A3, A4, A5, B1-B7, C1-C4. EPD Int GPI 5.0.1 (Section A.3.1) defaults to the A-D module structure. | The original finding falsely claimed PEP and modern EPD Int. use Upstream/Core/Downstream. They use or directly map to the A-D modular structure. However, hardcoding `includesA1_A3` as boolean properties remains an inflexible anti-pattern for extensible modelling. | Update the architectural justification: remove claims of incompatibility with PEP, but maintain the recommendation to replace booleans with an extensible module declaration structure. |
| **Module status semantics absent** (0.0 ≠ NotApplicable) | CONFIRMED | EN 15804 (via EPD Int GPI 5.0.1 Section 7.2) requires "ND" (Not Declared). PEP PCR Ed.4 uses explicit exclusions. | Missing data, excluded modules, and actual zero values must be distinguishable. A `0.0` value cannot represent "Module Not Declared". | Introduce a `moduleStatus` mechanism (e.g., Declared, Not Declared, Not Relevant). |
| **Resource use indicators absent** | CONFIRMED | PEP PCR Ed.4 (Section 2.10.1, p. 32) lists mandatory "Resource use indicators" (e.g., renewable/non-renewable primary energy). WAGO mapping shows `{}`. | The omission of LCI resource use indicators breaks compliance with all major Type III EPD programs. | Add the missing LCI resource use indicators to the submodel template. |
| **Result category discriminator absent** (LCI vs LCIA conflation) | CONFIRMED | PEP PCR Ed.4 (p. 31-33) strictly categorises results into: Environmental impact (LCIA), Resource use (LCI), Waste (LCI), Output flows (LCI). | Grouping all outputs under `lciaResults` is factually incorrect for LCI flows (waste, resources) and prevents downstream tools from safely aggregating impacts. | Rename `lciaResults` to `environmentalResults` and introduce a `resultCategory` classification. |
| **Product composition missing** | CONFIRMED WITH MODIFICATION | PEP PCR Ed.4 (Section 4.2, p. 41) mandates declaring constituent materials (mass/percentage). EPD Int GPI 5.0.1 (Section 7.4.5) mandates content declaration. | Content declaration is a core, mandatory requirement for EPDs, not merely an "optional extension" as proposed in the original target architecture. | Introduce a `ContentDeclaration` SMC as a standard, expected part of the EPD core structure, not an optional extension. |
| **`representativenessReference` contains ILCD/LCA tool artefacts** | CONFIRMED WITH MODIFICATION | EPD Int GPI 5.0.1 and PEP PCR dictate methodological reporting (e.g., reference year, software, database) but do NOT dictate internal database UUIDs like `referenceFlow.id`. | `referenceFlow.id` and `pictogramSource` are ILCD/openLCA implementation artefacts, not normative EPD exchange concepts. Other fields (like `referenceYear`) are valid but miscategorised. | Remove tool-specific UUIDs and image links. Refactor the remaining legitimate methodological fields into an `lcaMethodology` section. |
| **Missing ConceptDescription ValueLists** (Indicator/Module codes) | CONFIRMED | Both PEP and EPD Int define strict taxonomies for indicators and modules. Free-text strings prevent machine interoperability. | Relying on unconstrained `xs:string` for `indicatorCode` guarantees that different generators will use different string casings/formats, destroying interoperability. | Use IDTA ConceptDescriptions (or external URIs) for standardised indicators and modules, while allowing extensibility. |
| **Missing Functional Unit** | CONFIRMED | PEP PCR Ed.4 (p. 10) states: "The declarant party shall systematically use the functional unit... The declared unit can be used in addition." | The model provides `declaredUnit` but lacks the normative distinction between Functional Unit (quantified performance) and Declared Unit (quantity of product). | Introduce distinct modeling for Functional Unit vs. Declared Unit within the submodel. |
| **Product classification missing** | CONFIRMED WITH MODIFICATION | EPD Int GPI 5.0.1 (Section 7.4.4) mandates UN CPC code and recommends others (GTIN, CPV). | While EPDs require classification for routing/discovery, duplicating this entirely in the EPD submodel risks drifting from the AAS `Nameplate` submodel. | Add a lightweight classification reference in the EPD submodel, or define rules to inherit/reference the AAS Nameplate classification. |
| **Multi-product architecture absent** | REVISE | Both programs allow one EPD to cover a product family (e.g., via extrapolation or average results). | The submodel must support an EPD that covers a product family. However, this does not necessarily mean duplicating all product variants inside the EPD submodel itself. The EPD submodel is an attribute of the Asset; if the EPD covers a family, the submodel simply describes the scope of that EPD. | Provide a mechanism to declare that the EPD is a "Representative", "Average", or "Family" EPD, and link to the covered product identifiers. |
| **Placeholder Semantic IDs** (`http://example.com/`) | CONFIRMED | IDTA drafting rules prohibit publishing standard models with placeholder URIs. | The model is structurally incomplete until proper IDTA or standard URIs are minted. | SAFE TO IMPLEMENT NOW: Replace all placeholders with provisional IDTA URIs. |

---

## 2. Architecture decisions requiring working-group agreement

### Decision 1: Lifecycle / Module Representation
**What needs to be decided?** How should the AAS model represent the lifecycle modules covered by the EPD, replacing the current hard-coded `includesA1_A3` booleans?
**Why it matters:** Hard-coded booleans cannot express individual modules (e.g., A1 separate from A2) and cannot easily adapt to future PCR changes or alternative lifecycle structures.
*   **Option A: Repeatable `ModuleDeclaration` entries.** A list of declared modules (e.g., A1, A2, A3, B1) with their status (Declared, Not Declared).
    *   *Advantage:* Highly extensible; easily supports any PCR's nomenclature.
    *   *Disadvantage:* Slightly more verbose than booleans.
*   **Option B: Implicit declaration via Results.** Do not declare the boundary separately; instead, infer the boundary by looking at which modules exist in the `environmentalResults` array.
    *   *Advantage:* DRY (Don't Repeat Yourself); guarantees that the declared boundary matches the actual data.
    *   *Disadvantage:* A module might be "Declared" but have a value of 0.0, making it hard to distinguish from an omitted module unless status flags are added to every single result.
*   **Recommendation:** **Option A**. A dedicated `DeclaredModules` SMC provides a clear, machine-readable summary of the EPD's scope without forcing a consumer to parse the entire results array.
*   **Source constraints:** Programs require clear statements of the system boundary and which modules are Not Declared.
*   **Architectural freedom:** The exact data structure (list vs array of objects) is an AAS design choice.

### Decision 2: Module Status Semantics
**What needs to be decided?** How to represent the status of a module (e.g., missing data, zero impact, excluded by PCR).
**Why it matters:** A numeric value of `0.0` is ambiguous. It could mean "calculated zero", "not relevant", or "not declared".
*   **Option A: Generic State Enum + Optional Specific Code.** Use a generic AAS enum (`Declared`, `NotDeclared`, `NotRelevant`) and an optional `programmeSpecificCode` string (e.g., "MND", "MNR", "INA").
    *   *Advantage:* Standardises the logic for downstream consumers while preserving the exact terminology of the source EPD.
*   **Option B: Programme-Specific Strings only.** Just use an `xs:string` field for status.
    *   *Advantage:* Simple.
    *   *Disadvantage:* Zero interoperability; machines must learn every program's acronyms.
*   **Recommendation:** **Option A**.
*   **Source constraints:** EN 15804 uses ND, MND, MNR.
*   **Architectural freedom:** The AAS can define a unifying upper ontology (the generic state) mapped over the specific codes.

### Decision 3: Environmental Result Architecture
**What needs to be decided?** How to distinguish Impact Categories (GWP) from Inventory Flows (Resource Use, Waste).
**Why it matters:** Summing LCI flows with LCIA impacts is a critical semantic error.
*   **Option A: Single list with a `resultCategory` discriminator.** Keep a single `environmentalResults` list, but add an enum: `ImpactCategory`, `ResourceUse`, `Waste`, `OutputFlow`.
    *   *Advantage:* Keeps the model flat and simple.
*   **Option B: Separate collections.** Create `impactIndicators`, `resourceUseIndicators`, `wasteIndicators`, `outputFlowIndicators` as separate SMLs.
    *   *Advantage:* Structurally prevents mixing LCI and LCIA; perfectly aligns with EN 15804 / PEP reporting tables.
    *   *Disadvantage:* Deeper hierarchy.
*   **Recommendation:** **Option B**. It forces strict semantic separation and mirrors how EPDs are actually published in tables.
*   **Source constraints:** Source documents explicitly separate these categories in their reporting formats.
*   **Architectural freedom:** Both options are technically valid AAS models.

### Decision 4: Indicator Vocabulary Strategy
**What needs to be decided?** How to define the `indicatorCode` (e.g., "GWP-total") to ensure machine readability without breaking extensibility.
**Why it matters:** Free text strings (`GWP_tot`, `GWP-total`) break automated data exchange.
*   **Option A: Closed Enum/ValueList.** Hardcode all EN 15804 and PEP indicators into a fixed ConceptDescription ValueList.
    *   *Advantage:* Perfect validation.
    *   *Disadvantage:* Requires a new AAS Submodel version every time a PCR adds a new indicator.
*   **Option B: External URI Reference.** Use `SemanticId` pointing to an external vocabulary (e.g., an IDTA-hosted RDF/JSON-LD vocabulary or ECLASS).
    *   *Advantage:* Infinitely extensible without changing the AAS schema.
*   **Recommendation:** **Option B**, combined with a formally maintained IDTA EPD dictionary.
*   **Source constraints:** None on the technical implementation.
*   **Architectural freedom:** Standard semantic web vs. internal AAS ValueLists.

### Decision 5: Multi-Product / Product-Family Modelling
**What needs to be decided?** How should the EPD Submodel handle an EPD that covers a product family with extrapolation rules?
**Why it matters:** The AAS represents a specific asset. The EPD may represent a family.
*   **Option A: Embed all family data in the Submodel.** Replicate the entire extrapolation table (from the PEP) inside the AAS Submodel.
*   **Option B: Reference the EPD Scope.** The Submodel declares the EPD's scope (`productType`: "Family Average" or "Representative"), but provides the calculated impacts *specifically for the Asset the AAS represents*.
*   **Recommendation:** **Option B**. The AAS Submodel should deliver the data for *this specific asset*. If extrapolation was required to get this asset's data from a family EPD, the Submodel should present the final extrapolated results, linking back to the original EPD registration number as proof. Embedding generic extrapolation tables inside a specific Asset's shell breaks the Asset Administration Shell paradigm.

---

## 3. Action Plan

### SAFE TO IMPLEMENT NOW
*   Fix the comma bug in the semantic ID: `http://example.com/epd/lca,StandardsPcr` -> `http://example.com/epd/lcaStandardsPcr` (or replace with IDTA provisional URI).
*   Remove all `http://eclass.example.com/` and `http://example.com/` placeholder URIs and replace them with provisional `https://admin-shell.io/idta/EPD/...` URIs.
*   Remove the purely tool-specific ILCD fields: `referenceFlow.id` and `pictogramSource`.

### READY FOR DESIGN DECISION
*   Replace `systemBoundary` booleans with a structural module declaration.
*   Rename `lciaResults` and implement semantic separation (LCI vs LCIA).
*   Add `moduleStatus` to result values.
*   Add `ContentDeclaration` (Product and Packaging composition).
*   Add Functional Unit concepts alongside Declared Unit.

### NOT YET JUSTIFIED
*   The claim that PEP and EPD Int. use `Upstream/Core/Downstream` instead of the A-D module structure was factually incorrect. The A-D modularity concept remains valid and should be used as the structural baseline.
*   The claim that the EPD submodel must internally handle multi-product families is rejected. The AAS submodel should provide the specific environmental data for the specific Asset it describes, referencing the Family EPD it was derived from.
