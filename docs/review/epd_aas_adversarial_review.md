# Adversarial Architectural Review: AAS EPD Type III Submodel

**Review date:** 2026-09-10
**Reviewer role:** Adversarial data-model architect (Grill Me session)
**Repository:** [`epd-type-iii-submodel`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel)

**Artefacts inspected (ground truth):**
- [`model/template/epd-type-iii-submodel-template.aasx`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/model/template/epd-type-iii-submodel-template.aasx)
- [`examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx)
- [`docs/model/epd-type-iii-model.puml`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/docs/model/epd-type-iii-model.puml) + all section PUMLs
- [`docs/open-design-decisions.md`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/docs/open-design-decisions.md) (27 ODDs reviewed)
- [`docs/interoperability-mapping.md`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/docs/interoperability-mapping.md)
- [`examples/wago-00001/mapping/wago-00001-to-epd-submodel-mapping.json`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/examples/wago-00001/mapping/wago-00001-to-epd-submodel-mapping.json)
- [`docs/review/epd-type-iii-submodel-change-review.md`](file:///c:/Users/u0129589/OneDrive%20-%20WAGO/Python%20Skripte/Wago/aas_excel_conversion/epd-type-iii-submodel/docs/review/epd-type-iii-submodel-change-review.md)
- Reference documents: `docs/PEP Ecopassport/` and `docs/EPD International/`

---

## A. Executive Verdict

### Overall assessment

The model has undergone useful structural work. The move from static hardcoded indicator collections to a generic `lciaResults [SML]` with dynamic `idShort` instantiation is architecturally correct. The adoption of IDTA ContactInformation semantics for organisations, VDI 2770 document ID semantics, and a repeatable `lifeCyclePhaseValues [SML]` per indicator are all defensible choices.

However, **the model is not ready for release** as a programme-independent EPD data exchange layer. The problems are not cosmetic — they concern the core data model:

1. **Missing result category discriminator:** LCIA impact categories, LCI resource use, waste flows, and output flows are all collapsed into one unclassified `lciaResults [SML]`.
2. **Resource use indicators are entirely absent** — confirmed by `"resource_uses": {}` in the WAGO instance mapping.
3. **Module status is absent** — a value of 0.0 for a declared module and an excluded module are indistinguishable.
4. **`systemBoundary` hardwires the EN 15804 module grouping** — PEP ecopassport and EPD International non-construction use Upstream/Core/Downstream/Total, which is structurally incompatible.
5. **`representativenessReference` is an ILCD/openLCA database artefact** — `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, and `flowDiagramSource` are internal LCA tool properties with no place in a downstream EPD exchange model.
6. **No controlled vocabularies** for `indicatorCode`, `lifeCyclePhase`, or `unit`.
7. **Product composition is absent** — the WAGO source has a full material composition table; the AAS model has nothing.
8. **No product classification** — downstream routing, aggregation, and filtering is impossible.
9. **12+ `http://example.com/` and `http://eclass.example.com/` placeholder semantic IDs** — model is machine-unresolvable as-is.
10. **No multi-product architecture** — a product family or EPD covering multiple variants cannot be modelled.

> [!CAUTION]
> All three lossless representation tests FAIL. The model cannot serve as a generic EPD data exchange layer for PEP, EPD International non-construction, or EN 15804 construction without structural changes.

### Ratings (0–100%)

| Dimension | Score | Primary reason for score |
|---|---|---|
| Semantic completeness | **42%** | Resource use absent; module status absent; content declaration absent; functional unit absent; no product classification |
| Programme independence | **48%** | `systemBoundary` hardwires EN 15804 groupings; ILCD artefacts in `representativenessReference` |
| Extensibility | **62%** | `lciaResults [SML]` and `lifeCyclePhaseValues [SML]` are extensible; `systemBoundary` boolean flags are not |
| Downstream interoperability | **45%** | No controlled vocabularies; no module status; no result category; unit not resolvable at value level |
| Machine readability | **40%** | Uncontrolled free strings for all critical fields; placeholder semantic IDs; no ConceptDescription ValueLists |
| PEP ecopassport compatibility | **50%** | Impact indicators mappable; Upstream/Core/Downstream/Total not representable; composition absent; resource use absent |
| EPD Int. non-construction compatibility | **38%** | Lifecycle structure fundamentally incompatible; resource use absent; never tested against this programme |
| EPD Int. construction / EN 15804 compatibility | **58%** | A/B/C/D broadly representable; but module status absent; resource use absent; biogenic carbon misplaced |

---

## B. Requirement and Gap Matrix

### B.1 EPD Identification and Metadata

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| ISO 14025 §8.1.2 | EPD registration number | `identificationPublication/documentIds[isPrimary=true].documentIdentifier` | Covered | — | Generic EPD core | Keep. Well-modelled via VDI 2770. |
| ISO 14025 §8.1.2 | EPD version / revision | `identificationPublication/programOperatorVersion` | Partially covered | Medium | Generic EPD core | Rename to `epdVersion` — the current name conflates version with programme operator. |
| All sources | Programme operator identity | `programOperatorVerification/programOperator [ContactInformation]` | Covered | — | Generic EPD core | Keep. |
| ISO 14025 §8.1.4 | Manufacturer / EPD owner | `manufacturerProduct/manufacturerName [MLP]` | Covered | — | Generic EPD core | Keep. |
| EPD Int. GPI 5.0.1 §6 | LCA practitioner / EPD commissioner | `programOperatorVerification/epdDeveloper` | Partially covered | Medium | Generic EPD core | `epdDeveloper` is ambiguous — could be commissioning entity, LCA practitioner, or both. Add a `role [enum]` qualifier or split into separate roles. |
| ISO 14025 §6.7 | Declared unit | `manufacturerProduct/declaredUnit` | Covered | — | Generic EPD core | Keep. De-duplicate (two parallel definitions exist — see D.10). |
| **ISO 14025 §6.7** | **Functional unit** | **Missing** | **Missing** | **High** | **Generic EPD core** | **Normative distinction from declared unit is absent. A bare `referenceServiceLife` decimal is not a functional unit.** |
| ISO 14025 §6.4 | Reference service life | `manufacturerProduct/referenceServiceLife` | Partially covered | Medium | Generic EPD core | `xs:decimal` with implicit unit of years. Unit must be made explicit. |
| EPD Int. GPI 5.0.1 §7 | Geographical scope | `systemBoundary/geographicScope [xs:string]` | Partially covered | Medium | Generic EPD core | No coding scheme (ISO 3166-1 / UN M49). Also duplicates `applicableJurisdictions [SML]` in `manufacturerProduct`. |
| All sources | Date of issue | `identificationPublication/dateOfIssue [xs:date]` | Covered | — | Generic EPD core | Keep. ODD-17 (partial dates) must be resolved. |
| All sources | Validity date | `identificationPublication/validUntil [xs:date]` | Covered | — | Generic EPD core | Keep. Same ODD-17 concern. |
| All sources | EPD languages | `identificationPublication/languages [SML]` | Covered | — | Generic EPD core | Keep. |
| All sources | Declaration URL | `identificationPublication/declarationUrl [xs:string]` | Covered | — | Generic EPD core | Change `xs:string` → `xs:anyURI`. |
| **All sources** | **Product classification (ECLASS, UN CPC, ETIM, EC3)** | **Missing** | **Missing** | **High** | **Generic EPD core** | **Without classification, downstream routing, aggregation, and filtering is impossible. Add `productClassifications [SML]`.** |
| PEP PCR Ed.4 §4.2 | Single product article number | `manufacturerProduct/productArticleNumberOfManufacturer [Property]` | Partially covered | High | Generic EPD core | Cannot represent product families. Replace with `productIds [SML]`. |
| All sources | Multiple article numbers / product family | Not supported | Missing | High | Generic EPD core | ODD-07 and ODD-22 defer this — but it is the dominant use case in the WAGO context. |
| All sources | Source data provenance format | `identificationPublication/sourceDataFormat` | Covered | — | Implementation-specific | Consider moving outside EPD content to AAS administration (ODD-18). |

### B.2 Product and Content Declaration

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| **PEP PCR Ed.4 §5.3** | **Product material composition table** | **Missing** | **Missing** | **Blocker** | **Generic EPD core** | **The WAGO source JSON has a full product composition table (material, mass, mass%, CAS, recycled content, material type). Entirely absent from AAS. Critical for DPP, ESPR, REACH, EN 50693.** |
| PEP PCR Ed.4 §5.3 | Packaging composition table | Missing | Missing | High | Generic EPD core | Same gap for packaging. |
| EN 15804 §6.3 | Recycled input content (%) | Missing | Missing | High | Generic EPD core | Required by EN 15804 and EPD Int. GPI. Absent. |
| All sources | Mass per declared unit | `manufacturerProduct/massPerDeclaredUnit [xs:decimal]` | Covered | — | Generic EPD core | Keep. Unit (kg) is implicit — make it explicit. |
| EN 15804 Annex D | Biogenic carbon content in product (kg C) | `manufacturerProduct/biogenicCarbonContent/biogenicCarbonContentProduct` | Covered | — | Generic EPD core | Keep interim. ODD-25 correctly identifies misplacement. Should move to `additionalEnvironmentalInformation`. |
| EN 15804 Annex D | Biogenic carbon content in packaging (kg C) | `manufacturerProduct/biogenicCarbonContent/biogenicCarbonContentPackaging` | Covered | — | Generic EPD core | Keep interim. Same relocation recommendation. |
| **PEP PSR-0001 Ed.4 §5** | **Hazardous substances / SVHC / IEC 62474** | **Missing** | **Missing** | **High** | **Generic EPD core** | **Mandatory for electronics EPDs (EU REACH, RoHS, IEC 62474). Completely absent.** |
| All sources | Multiple products / product variants | Not supported | Missing | Blocker | Generic EPD core | Fundamental cardinality error. ODD-07 and ODD-22 defer this unjustifiably. |
| EPD Int. GPI 5.0.1 | Product representativeness type | Missing | Missing | High | Generic EPD core | No mechanism to declare Representative / Average / Worst-case. |
| **PEP PCR Ed.4 §5.4** | **Extrapolation/multiplication factors per variant** | **Missing** | **Missing** | **High** | **Generic EPD core** | **WAGO source has a full extrapolation table (A1A2A3, A4, A5, B, C, D factors per product). Absent from AAS.** |
| All sources | Manufacturing site structure | `manufacturerProduct/manufacturingSites [SML]` | Partially covered | Medium | Generic EPD core | SML defined but element structure unspecified — no child properties defined in the model. |

### B.3 Lifecycle Structure (Critical)

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| **EN 15804 module groupings (fixed)** | `systemBoundary` boolean flags: `includesA1_A3`, `includesA4_A5`, `includesB1_B7`, `includesC1_C4`, `includesD` | `systemBoundary` (5 booleans) | **Partially covered** | **Blocker** | **EN 15804-specific** | **These five booleans encode the EN 15804 module grouping as fixed structural properties. Replace with `declaredModules [SML]`.** |
| **PEP PCR Ed.4 §6** | **Upstream / Core / Downstream / Total** | **Not representable** | **Missing** | **Blocker** | **Generic EPD core** | **The PEP lifecycle frame is fundamentally incompatible with the boolean flag structure. The model cannot serve PEP EPDs without structural redesign.** |
| **EPD Int. non-construction** | **Upstream / Core / Downstream / Total** | **Not representable** | **Missing** | **Blocker** | **Generic EPD core** | **Same structural incompatibility as PEP.** |
| EN 15804 | Module D (beyond system boundary) | `includesD [boolean]` | Partially covered | Medium | EN 15804-specific | A boolean is insufficient. Module D has specific normative meaning distinct from within-boundary modules. |
| **All sources** | **Module status: Declared / NotApplicable / Excluded / Aggregated** | **Missing** | **Missing** | **Blocker** | **Generic EPD core** | **ODD-10 acknowledged but unresolved. A result value of 0.0 is indistinguishable from NotApplicable or Excluded. This is semantically critical for any downstream aggregation.** |
| All sources | Lifecycle phase controlled vocabulary | `lifeCyclePhase [xs:string]` — free text | Missing | Blocker | Generic EPD core | `A1-A3` and `A1A2A3` and `manufacturing` are all syntactically valid — semantically indistinguishable without a controlled vocabulary. |

### B.4 Environmental Performance Results

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| All sources | Result value per indicator × lifecycle phase | `lciaResults[]/lifeCyclePhaseValues[]/value [xs:decimal]` | Covered (structurally) | — | Generic EPD core | The generic repeatable structure is architecturally correct. |
| **All sources** | **Indicator code controlled vocabulary** | **`indicatorCode [xs:string]` — free text** | **Missing** | **High** | **Generic EPD core** | **No ConceptDescription ValueList. `GWP-total`, `GWP_total`, `GWP Total` are all valid — no machine can distinguish them.** |
| EN 15804 | Mandatory vs. optional vs. additional indicators | `indicatorGroup [xs:string]` — free text | Partially covered | High | EN 15804-specific | No controlled vocabulary. Groups LCIA/LCI/Additional are EN 15804-specific. Replace with `resultCategory [enum]`. |
| All sources | LCIA method / characterisation factors | `indicatorStandard [xs:string]` — free text | Partially covered | High | Generic EPD core | Per-indicator, not per-LCA-study. The overall LCIA method should be declared at submodel level. |
| ODD-15 | Unit not linked to individual result value | Unit on indicator level only | Partially covered | High | Generic EPD core | A consumer reading only `value` has no direct link to unit. `characterizationUnit` must be navigated from parent. |
| **All sources** | **Null / NotApplicable value semantics** | **Not representable** | **Missing** | **Blocker** | **Generic EPD core** | **`xs:decimal` cannot represent null or NotApplicable. Missing entry ≠ NotApplicable.** |

### B.5 Resource Use, Waste and Output Flows (Critical)

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| **EN 15804 / EPD Int.** | **PERE, PERM, PERT, PENRE, PENRM, PENRT, SM, RSF, NRSF, FW (resource use)** | **`"resource_uses": {}` in WAGO mapping — confirmed empty** | **Missing** | **Blocker** | **Generic EPD core** | **The WAGO instance mapping confirms resource use is completely empty. These are EN 15804 Table 2 indicators, mandatory in all major EPD programmes. Absent from the model entirely.** |
| EN 15804 / EPD Int. | HWD, NHWD, RWD (waste indicators) | Presumably in `lciaResults` | Ambiguous | High | Generic EPD core | Waste indicators are LCI inventory results, NOT LCIA characterization results. Placing them in `lciaResults` is semantically incorrect. Separate `inventoryResults` section needed. |
| EN 15804 | CRU, MFR, MER, EEE, EET (output flows) | Presumably in `lciaResults` | Ambiguous | High | Generic EPD core | Same issue. Output flows ≠ LCIA impact categories. |
| All sources | Semantic distinction between result types | All in `lciaResults [SML]` | Missing | Blocker | Generic EPD core | A discriminator `resultCategory [enum: ImpactCategory/ResourceUse/WasteFlow/OutputFlow]` is required per result entry. |
| EPD Int. non-construction | PERT = PERE + PERM aggregate relationship | Not representable | Missing | Medium | Generic EPD core | Aggregation relationship is not machine-representable. |

### B.6 LCA Methodology

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| ISO 14044 / EPD Int. GPI | LCA software name + version | Missing (ODD-09) | Missing | High | Generic EPD core | Add structured `lcaSoftware [SMC]`: `name`, `version`. |
| ISO 14044 / EPD Int. GPI | Background LCA database + version | Missing (ODD-09) | Missing | High | Generic EPD core | Add `lcaDatabase [SMC]`: `name`, `version`, `provider`. |
| ISO 14044 | Overall LCIA method | Per-indicator `indicatorStandard` only | Partially covered | High | Generic EPD core | Declare at submodel level. |
| ISO 14044 | Machine-readable system boundary type | `systemBoundary/technologyCoverage [xs:string]` | Partially covered | Medium | Generic EPD core | Add `systemBoundaryType [enum: CradleToGate/CradleToGrave/GateToGrave/...]`. |
| ISO 14044 | Allocation approach | Missing | Missing | Medium | Generic EPD core | Add `allocationApproach [MLP]`. |
| ISO 14044 | Cut-off rules | Missing | Missing | Medium | Generic EPD core | Add `cutOffRules [MLP]`. |
| EPD Int. GPI §6 | Reference year for background data | `representativenessReference/referenceYear` | Covered | — | Generic EPD core | Keep, but move to `lcaMethodology`. |
| EPD Int. GPI | Primary data share (%) | Missing | Missing | Medium | Generic EPD core | Increasingly required by EPD programmes and DPP. |
| EN 15804 | Electricity model / grid mix | `representativenessReference/energyModel [xs:string]` | Partially covered | Medium | Generic EPD core | Free text in wrong section. Should be structured `electricityModel [SMC]`. |

### B.7 Verification

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| ISO 14025 §8.1.6 | Third-party verifier identity | `programOperatorVerification/thirdPartyVerifier [ContactInformation]` | Covered | — | Generic EPD core | Keep. |
| PEP PCR Ed.4 | Verifier accreditation ID | `thirdPartyVerifier/verifierAccreditationId` | Covered | — | Generic EPD core | Keep. |
| ISO 14025 §8.1.6 | Verification statement URL | `thirdPartyVerifier/verificationStatementUrl` | Covered | — | Generic EPD core | Keep. |
| **ISO 14025 §8.1.6** | **Verification type: Individual / Pre-verified tool / Process certification** | **Missing** | **Missing** | **High** | **Generic EPD core** | **EPD Int. GPI formally distinguishes these — different assurance levels. Absent from model.** |
| **EPD Int. GPI** | **Verification date** | **Missing** | **Missing** | **High** | **Generic EPD core** | **Distinct from `dateOfIssue`. When was the EPD verified? Absent.** |

### B.8 The `representativenessReference` Section (Critical)

> [!CAUTION]
> This entire section appears to be an ILCD/openLCA database artefact that was imported into the AAS model because the first populated instance was generated via an openEPD intermediary. It should be restructured into a proper `lcaMethodology [SMC]`.

| Source | Concept | Current AAS path | Status | Severity | Classification | Recommendation |
|---|---|---|---|---|---|---|
| **ILCD / openLCA** | **`referenceFlow.id`** | **`representativenessReference/referenceFlow.id`** | **Overmodelled** | **Blocker** | **Implementation-specific** | **Internal openLCA/ILCD database UUID. Not an EPD concept. Remove.** |
| **ILCD / openLCA** | **`referenceFlow.amount`** | **`representativenessReference/referenceFlow.amount`** | **Overmodelled** | **Blocker** | **Implementation-specific** | **LCA model concept. The declared unit already captures this. Remove.** |
| **ILCD format** | **`pictogramSource`, `flowDiagramSource`** | **`representativenessReference/pictogramSource`, `flowDiagramSource`** | **Overmodelled** | **High** | **Implementation-specific** | **ILCD image path properties — LCA tool artefacts. Not EPD exchange data. Remove.** |
| ILCD / openLCA | `dataSetValidUntil` | `representativenessReference/dataSetValidUntil` | Ambiguous | Medium | Implementation-specific | Duplicates `validUntil`. ILCD database concept, not EPD concept. Remove. |
| EPD Int. GPI | Technology description | `representativenessReference/technologyDescription` | Partially covered | Medium | Generic EPD core | Legitimate concept, wrong parent. Move to `lcaMethodology`. |
| EPD Int. GPI | Time representativeness description | `representativenessReference/timeRepresentativenessDescription` | Covered | — | Generic EPD core | Legitimate. Move to `lcaMethodology`. |
| EPD Int. GPI | Geographical description, location | `representativenessReference/geographicalDescription`, `location` | Covered | — | Generic EPD core | Duplicates `geographicScope` in `systemBoundary`. Consolidate in `lcaMethodology`. |
| — | Section name `representativenessReference` | — | — | Blocker | — | Name does not correspond to any normative EPD concept. Rename to `lcaMethodology`. |

### B.9 Semantic Identifiers

| Semantic ID | Problem | Severity | Action |
|---|---|---|---|
| `http://eclass.example.com/referenceFlow.id` (Sem_040) | Fake ECLASS URI — machine-unresolvable | Blocker | Remove with the field |
| `http://eclass.example.com/referenceFlow.amount` (Sem_041) | Fake ECLASS URI | Blocker | Remove with the field |
| `http://eclass.example.com/referenceYear` (Sem_042) | Fake ECLASS URI | High | Assign IDTA working URI |
| `http://eclass.example.com/` (Sem_043–Sem_051) | 9 more fake ECLASS URIs | High | Replace with IDTA working URIs |
| `http://example.com/epd/programOperatorVerification` (Sem_014) | Placeholder on top-level section | High | Assign IDTA working URI |
| `http://example.com/epd/manufacturerProduct` (Sem_022) | Placeholder on top-level section | High | Assign IDTA working URI |
| `http://example.com/epd/representativenessReference` (Sem_039) | Placeholder on top-level section | High | Remove with section rename |
| `http://example.com/epd/lca,StandardsPcr` (Sem_052) | **Contains a comma** — URI parsing bug | High | Fix bug + assign IDTA working URI |
| `indicatorCode` — no CD ValueList | Free text, cannot be validated | Blocker | Add ConceptDescription ValueList |
| `lifeCyclePhase` — no CD ValueList | Free text, cannot be validated | Blocker | Add ConceptDescription ValueList |

---

## C. Proposed Programme-Independent Semantic Core

### C.1 Proposed top-level structure

```
EPD Type III Submodel
├── EPDIdentification [SMC, mandatory]
│   ├── documentIds [SML]              ← keep VDI 2770 pattern
│   ├── epdVersion [Property]          ← rename from programOperatorVersion
│   ├── dateOfIssue [Property, xs:date]
│   ├── validUntil [Property, xs:date]
│   ├── languages [SML]
│   └── declarationUrl [Property, xs:anyURI]
│
├── ProgrammeAndPCR [SMC, mandatory]
│   ├── programOperator [ContactInformation]
│   ├── epdProgramme [Property]        ← NEW: named programme identifier
│   ├── standardsCompliance [SML]
│   └── productCategoryRules [SML]    ← with ruleType: PCR/c-PCR/PSR/programme-PCR
│
├── Verification [SMC, optional]
│   ├── thirdPartyVerifier [ContactInformation + EPD extensions]
│   ├── verifierAccreditationId [Property]
│   ├── verificationDate [Property, xs:date]      ← NEW
│   ├── verificationType [Property, enum]          ← NEW
│   └── verificationStatementUrl [Property, xs:anyURI]
│
├── ProductInformation [SMC, mandatory]
│   ├── manufacturer [ContactInformation]
│   ├── manufacturingSites [SML]       ← with structured child properties
│   ├── productName [MLP]
│   ├── productIds [SML]               ← NEW: replaces single article number
│   ├── productClassifications [SML]   ← NEW: ECLASS, UN CPC, ETIM, EC3...
│   ├── productDescription [MLP]
│   ├── productImage [File, optional]
│   ├── productType [Property, enum: Generic/Representative/Average/WorstCase]  ← NEW
│   └── productFamilyReference [Property, optional]  ← NEW
│
├── DeclaredUnit [SMC, mandatory]       ← de-duplicated from manufacturerProduct
│   ├── declaredQuantity [Property, xs:decimal]
│   ├── unitOfMeasure [Property, xs:string, controlled]
│   ├── massPerDeclaredUnit [Property, xs:decimal, kg]
│   ├── referenceServiceLife [Property, xs:integer, years]
│   └── functionalUnitDescription [MLP, optional]  ← NEW
│
├── ContentDeclaration [SMC, optional]  ← NEW section
│   ├── productComposition [SML]        ← NEW
│   ├── packagingComposition [SML]      ← NEW
│   ├── biogenicCarbonContentProduct [Property]   ← moved from manufacturerProduct
│   └── biogenicCarbonContentPackaging [Property] ← moved from manufacturerProduct
│
├── LCAMethodology [SMC, mandatory]    ← replaces systemBoundary + representativenessReference
│   ├── systemBoundaryType [Property, enum]       ← NEW
│   ├── declaredModules [SML]          ← REPLACES boolean flags
│   │   └── [ModuleDeclaration: moduleCode + moduleStatus]
│   ├── allocationApproach [MLP]       ← NEW
│   ├── cutOffRules [MLP]              ← NEW
│   ├── lcaSoftware [SMC]              ← NEW
│   ├── lcaDatabase [SMC]              ← NEW
│   ├── lciaMethod [Property]          ← NEW (submodel-level)
│   ├── referenceYear [Property, xs:gYear]
│   ├── timeRepresentativenessDescription [MLP]
│   ├── geographicalScope [Property, ISO 3166-1]
│   ├── geographicalDescription [MLP]
│   ├── technologyDescription [MLP]
│   └── primaryDataShare [Property, xs:decimal]   ← NEW
│
├── EnvironmentalResults [SML, mandatory]  ← rename from lciaResults
│   └── [ResultEntry SMC]
│       ├── resultCategory [Property, enum: ImpactCategory/ResourceUse/WasteFlow/OutputFlow]  ← NEW
│       ├── indicatorCode [Property, from CD ValueList]  ← add ValueList
│       ├── indicatorName [MLP]
│       ├── characterizationUnit [SMC]
│       ├── mandatory [Property, xs:boolean, optional]
│       └── moduleValues [SML]         ← rename from lifeCyclePhaseValues
│           └── [ModuleValue SMC]
│               ├── moduleCode [Property, from CD ValueList]  ← rename + add ValueList
│               ├── moduleStatus [Property, enum]             ← NEW
│               └── value [Property, xs:decimal]
│
├── AdditionalEnvironmentalInformation [SMC, optional]  ← NEW section
│   └── [SVHC, scenarios, etc.]
│
├── EPDDocumentReference [File, optional]
│
└── EPDProvenance [SMC, optional]
    ├── sourceDataFormat [Property]    ← moved from identificationPublication
    └── epdDeveloper [ContactInformation]
```

### C.2 What does NOT belong in the generic core

| Concept | Reason |
|---|---|
| `referenceFlow.id` | Internal ILCD/openLCA database UUID. LCA tool artefact, not EPD concept. |
| `referenceFlow.amount` | LCA model quantity. Declared unit already captures the reference amount. |
| `pictogramSource`, `flowDiagramSource` | ILCD image path properties — LCA software artefacts. |
| `dataSetValidUntil` (in representativenessReference) | Duplicates `validUntil`. ILCD artefact. |
| EPD publishing workflow status | Administrative — programme portal concern, not EPD content. |
| EPD programme portal flags (send-to-INIES, etc.) | Programme-specific administrative. |
| Billing contact, order number | ERP concern, outside scope. |
| `sourceDataFormat` inside EPD identification | AAS provenance metadata, not EPD content. Move to `EPDProvenance`. |
| Access control `private` flag | AAS ABAC/RBAC infrastructure concern (correctly removed per ODD-16). |

---

## D. Proposed Changes (Detail)

### D.1 Replace `systemBoundary` boolean flags with `declaredModules [SML]`

**Priority: Blocker**

| Item | Detail |
|---|---|
| Current path | `systemBoundary/includesA1_A3`, `includesA4_A5`, `includesB1_B7`, `includesC1_C4`, `includesD` (xs:boolean) |
| Proposed path | `lcaMethodology/declaredModules [SML]` |
| Element structure | Each entry: `moduleCode [Property, xs:string, CD ValueList]` + `moduleStatus [Property, enum: Declared/NotApplicable/Excluded/Aggregated]` |
| CD ValueList | A1, A2, A3, A1-A3, A4, A5, B1–B7 (individual + aggregate), C1–C4 (individual + aggregate), D, Upstream, Core, Downstream, Total |
| Backwards compatibility | Breaking. |
| Why | EN 15804 groupings (A1-A3, A4-A5, B1-B7, C1-C4, D) are hardwired as fixed booleans. PEP and EPD Int. non-construction use Upstream/Core/Downstream/Total — structurally incompatible without redesign. |

### D.2 Add `moduleStatus` to every result module entry

**Priority: Blocker**

Add `moduleStatus [Property, xs:string, enum: Declared/NotApplicable/Excluded/Aggregated]` to every `lifeCyclePhaseValues` entry. Without this, 0.0 and NotApplicable and Excluded are indistinguishable.

### D.3 Add `resultCategory` discriminator to each result entry

**Priority: Blocker**

Add `resultCategory [Property, enum: ImpactCategory/ResourceUse/WasteFlow/OutputFlow]` to each entry in `lciaResults`. Rename `lciaResults` → `environmentalResults` to reflect the broader semantic scope.

### D.4 Add `productComposition [SML]` and `packagingComposition [SML]`

**Priority: Blocker**

New `contentDeclaration [SMC]` containing:
- `productComposition [SML]`: each entry has `materialName [MLP]`, `mass_kg [Property, xs:decimal]`, `massPercent [Property, xs:decimal]`, `casNumber [Property, xs:string]`, `recycledContentPercent [Property, xs:decimal]`, `materialCategory [Property, xs:string]`
- `packagingComposition [SML]`: same structure

### D.5 Refactor `representativenessReference` → `lcaMethodology [SMC]`

**Priority: High**

Remove: `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, `flowDiagramSource`, `dataSetValidUntil`.
Retain and relocate: `referenceYear`, `timeRepresentativenessDescription`, `geographicalDescription`, `location`, `technologyDescription`, `technicalPurpose`, `energyModel`.
Add: `lcaSoftware [SMC]`, `lcaDatabase [SMC]`, `lciaMethod [Property]`, `allocationApproach [MLP]`, `cutOffRules [MLP]`, `systemBoundaryType [Property]`, `primaryDataShare [Property]`.

### D.6 Add ConceptDescription ValueLists for indicator codes and module codes

**Priority: High**

- `EPDIndicatorCode [CD ValueList]`: GWP-total, GWP-fossil, GWP-biogenic, GWP-luluc, ODP, AP, EP-marine, EP-freshwater, EP-terrestrial, POCP, ADP-fossil, ADP-elements, WDP, PM, IRP, ETP-fw, HTP-c, HTP-nc, SQP, PENRT, PENRE, PERT, PERE, PERM, PENRM, SM, RSF, NRSF, FW, HWD, NHWD, RWD, CRU, MFR, MER, EEE, EET
- `EPDLifeCycleModule [CD ValueList]`: A1, A2, A3, A1-A3, A4, A5, B1, B2, B3, B4, B5, B6, B7, B1-B7, C1, C2, C3, C4, C1-C4, D, Upstream, Core, Downstream, Total

### D.7 Replace `productArticleNumberOfManufacturer` with `productIds [SML]`

**Priority: High**

Each entry: `idType [enum: ArticleNumber/EAN/GTIN/ETIM/...]` + `idValue [xs:string]`.

### D.8 Add `verificationType` and `verificationDate`

**Priority: High**

`verificationType [Property, xs:string, enum: IndividualVerification/PreVerifiedTool/ProcessCertification]` + `verificationDate [Property, xs:date]`.

### D.9 Resolve all placeholder semantic IDs

**Priority: High**

Assign provisional IDTA-namespaced URIs (`https://admin-shell.io/idta/EPD/...`) for all sections currently using `http://example.com/` or `http://eclass.example.com/`. Fix the comma bug in `http://example.com/epd/lca,StandardsPcr`.

### D.10 De-duplicate `declaredUnit`

**Priority: Medium**

Two parallel `declaredUnit` abstractions exist with different property names (`quantity` vs. `declaredQuantity`, `unit` vs. `unitOfMeasure`). Consolidate into one canonical `DeclaredUnit [SMC]` at top level.

---

## E. Overfitting Review

| Overfit risk | Model element | Why overfit | Fix |
|---|---|---|---|
| **EN 15804** | `systemBoundary` boolean flags | Encodes exactly the EN 15804 aggregation groups. Not representable for PEP or EPD Int. non-construction. | Replace with `declaredModules [SML]` |
| **EN 15804** | `biogenicCarbonContent` inside `manufacturerProduct` | EN 15804 Annex D classifies biogenic carbon as Additional Environmental Information, not product data. | Move to `additionalEnvironmentalInformation [SMC]` |
| **PEP ecopassport / ILCD** | `referenceFlow.id`, `referenceFlow.amount` | Internal ILCD/openLCA identifiers introduced because WAGO PEP was mapped via openEPD/openLCA. | Remove both |
| **ILCD format** | `pictogramSource`, `flowDiagramSource` | ILCD format image path properties — LCA tool artefacts, not EPD exchange data. | Remove |
| **openEPD transport** | `sourceDataFormat` in `identificationPublication` | Describes AAS generation provenance, not EPD content. | Move to `EPDProvenance [SMC]` |
| **EN 15804** | `indicatorGroup [xs:string]` | LCIA/LCI/Additional groups are EN 15804-specific. PEP does not use this taxonomy. | Replace with `resultCategory [enum]` |
| **Single source (WAGO PEP)** | `programOperatorVersion` mandatory | WAGO PEP has a specific version string. Other programmes use different conventions or none. | Make optional |

---

## F. Lossless Semantic Representation Test

### F.1 PEP ecopassport (WAGO-00001-V01.01-EN)

| Information | In AAS? | Gap type |
|---|---|---|
| Registration number, issue date, validity | Yes | — |
| Programme operator, verifier, verifier accreditation | Yes | — |
| PCR reference | Yes | — |
| PSR not distinguished from PCR | Partial | PSR ≡ PCR structurally (ODD-26 open) |
| Product name, article number | Yes | — |
| Declared unit, mass, service life | Yes | — |
| **Product composition table** | **No** | **Semantic data missing (critical)** |
| **Packaging composition table** | **No** | **Semantic data missing** |
| **Extrapolation factor table** | **No** | **Semantic data missing** |
| Lifecycle phases A1-A3, A4, A5, B1-B7, D | Yes (free strings) | No controlled vocabulary, no status |
| **C1–C4 null — module status unknown** | **No** | **Module status missing (critical)** |
| Impact indicators (GWP, ODP, AP, etc.) | Representable | No controlled vocabulary |
| **Resource use indicators (PENRT, SM, FW, etc.)** | **No** | **Semantic data missing (confirmed `resource_uses: {}`)** |
| Waste / output flows (HWD, NHWD, MFR, EE...) | Partial | Semantic conflation with LCIA |
| **PEP lifecycle frame: Upstream/Core/Downstream/Total** | **No** | **Insufficient model structure** |

**Verdict: FAILS** — 6 critical gaps.

### F.2 EPD International – Non-construction

| Information | In AAS? | Gap type |
|---|---|---|
| Programme operator, PCR, c-PCR | Representable | — |
| **Upstream / Core / Downstream / Total lifecycle structure** | **No** | **Insufficient model structure** |
| Impact indicators | Representable | No controlled vocabulary |
| **Resource use (PENRT, PERT, SM, RSF, NRSF, FW)** | **No** | **Semantic data missing** |
| Waste / output flows | Partial | Semantic conflation |
| **Module status** | **No** | **Missing** |
| Product classification | No | Missing |

**Verdict: FAILS** — structurally incompatible lifecycle frame + resource use absent.

### F.3 EPD International – Construction / EN 15804

| Information | In AAS? | Gap type |
|---|---|---|
| Programme operator, PCR 2019:14 | Representable | — |
| EN 15804 module structure A1–D | Partial | Boolean flags; individual B-modules cannot be declared separately |
| Impact indicators (EF 3.0 full set) | Representable | No controlled vocabulary |
| **Module status: Declared / ND / MND / MNR** | **No** | **Missing (blocker)** |
| **Resource use: PERE, PERM, PERT, PENRE, PENRM, PENRT, SM, RSF, NRSF, FW** | **No** | **Semantic data missing** |
| Waste, output flows | Partial | Semantic conflation |
| Scenario declarations (C-scenarios) | No | Missing |
| Biogenic carbon (Annex D) | Partial | Wrong section |

**Verdict: FAILS** — module status and resource use missing are blockers.

---

## G. Downstream Usability Test

A downstream consumer with no knowledge of PEP, EPD International, or the source files receives the AAS instance.

| Consumer question | Reliably answerable? | Gap |
|---|---|---|
| What product is this? | Partially — name + article number, no classification | No `productClassification` |
| What EPD programme issued this? | Partially — programme operator present, no explicit programme name | No `epdProgramme` field |
| Which PCR applies? | Partially — PCR reference exists, no role taxonomy | No `ruleType` controlled vocab |
| Which LCIA method was used? | No — not declared at submodel level | `lciaMethod` absent |
| Which environmental indicator does this entry represent? | Only by convention — free string | No CD ValueList for `indicatorCode` |
| What unit applies to this result value? | Indirectly — must navigate to parent `characterizationUnit` | Unit not on value element |
| Is this unit machine-resolvable? | No — `unitId` namespace unresolved (ODD-04) | Placeholder URIs |
| Which lifecycle module does this apply to? | Only by convention — free string | No CD ValueList for `lifeCyclePhase` |
| Is this module declared, excluded, or not applicable? | No | Module status absent |
| Is the result verified? | Partially — verifier present, type + date absent | No `verificationType`, no `verificationDate` |
| What is the reference period for background data? | Buried — in wrong section | `referenceYear` in `representativenessReference` |
| Does this cover one product or a family? | No — single article number only | No product type or family architecture |
| What materials is the product made of? | No | `productComposition` absent |

**Downstream usability verdict:** 10 of 13 consumer questions cannot be answered reliably. External knowledge of the source programme is required to interpret the data.

---

## H. Recommended Target Architecture

```
LAYER 1 — Mandatory programme-independent EPD core
    EPDIdentification, ProgrammeAndPCR, ProductInformation,
    DeclaredUnit, LCAMethodology, EnvironmentalResults

LAYER 2 — Optional generic EPD extensions
    ContentDeclaration, Verification, AdditionalEnvironmentalInformation,
    EPDDocumentReference, EPDProvenance

LAYER 3 — PCR-specific extensions (optional SMC)
    Identified by ruleType + named convention
    Examples: PEP extrapolation table, EN 15804 scenario declarations,
              construction-specific additional environmental information

LAYER 4 — Programme-specific extensions (optional SMC)
    Identified by programme ID
    Examples: PEP portal metadata, EPD Int. platform distribution flags

LAYER 5 — Other AAS Submodels (not part of EPD Submodel)
    IDTA Nameplate — basic product identification (avoid duplication)
    IDTA ContactInformation — already reused (correct)
    IDTA Carbon Footprint — if DPP requires separate carbon declaration

LAYER 6 — Outside the AAS EPD model
    EPD publishing workflow state
    Access control / private flag (AAS ABAC/RBAC)
    Billing, order data (ERP)
    Distribution channel flags (portal)
    Full LCA project files (LCA software)
```

**Evolutionary vs. redesign recommendation:**

- **Evolutionary** (backwards-compatible additions): Add `resultCategory`, `moduleStatus`, `verificationType`, `verificationDate`, `productClassifications`, ConceptDescription ValueLists, `contentDeclaration`.
- **Structural redesign** (breaking, necessary): Replace `systemBoundary` boolean flags; rename/refactor `representativenessReference` → `lcaMethodology`; remove ILCD artefacts; rename `lciaResults` → `environmentalResults`.

---

## I. Top 10 Changes Before Release

### #1 — Add `moduleStatus` to every result module entry
**What is wrong:** A result value of 0.0 and a module status of NotApplicable are indistinguishable. Every downstream aggregation, comparison, and EPD completeness check fails without this.
**Why it matters:** ISO 14044 / EN 15804 normatively distinguish Declared / NotApplicable / Excluded / Aggregated. All three tested programmes use this distinction.
**Change:** Add `moduleStatus [Property, enum: Declared/NotApplicable/Excluded/Aggregated]` to every `LifeCyclePhaseValue` entry.
**References:** EN 15804:2019+A2 Table A.1. EPD Int. PCR 2019:14. PEP PCR Ed.4.

---

### #2 — Replace `systemBoundary` boolean flags with `declaredModules [SML]`
**What is wrong:** Five hardwired booleans (`includesA1_A3`, `includesA4_A5`, `includesB1_B7`, `includesC1_C4`, `includesD`) encode the EN 15804 lifecycle grouping as fixed structural properties.
**Why it matters:** PEP ecopassport and EPD International non-construction use Upstream/Core/Downstream/Total — structurally incompatible. The model cannot serve ~40% of EPDs without redesign.
**Change:** Replace with `declaredModules [SML]` containing `ModuleDeclaration [SMC]` entries: `moduleCode [CD ValueList]` + `moduleStatus [enum]`.
**References:** PEP PCR Ed.4 §6. EPD Int. non-construction indicator workbook.

---

### #3 — Add `productComposition [SML]` with material composition data
**What is wrong:** The WAGO source has a full material composition table (material, mass, mass%, CAS, recycled content, material type). The AAS model has nothing. Product composition is entirely absent.
**Why it matters:** ESPR, EU Digital Product Passport, EN 50693, REACH SVHC, and supply chain due diligence all require material composition. This is not optional for electronics.
**Change:** Add `contentDeclaration [SMC]` containing `productComposition [SML]` and `packagingComposition [SML]`.
**References:** PEP PCR Ed.4 §5.3. WAGO source mapping `product_composition` table. EU ESPR Regulation.

---

### #4 — Add `resultCategory` discriminator and rename `lciaResults` → `environmentalResults`
**What is wrong:** LCIA impact categories (GWP), LCI resource use (PENRT), LCI waste flows (HWD), and LCI output flows (CRU) are all collapsed into one undifferentiated `lciaResults [SML]`. The name is factually wrong for 50%+ of the entries.
**Why it matters:** Downstream tools that sum LCIA results must not accidentally include HWD in the sum. The conflation introduces interpretation errors.
**Change:** Add `resultCategory [Property, enum: ImpactCategory/ResourceUse/WasteFlow/OutputFlow]` to each result entry. Rename `lciaResults` → `environmentalResults`.
**References:** EN 15804 three-table structure. EPD Int. indicator workbook three-table structure.

---

### #5 — Add ConceptDescription ValueLists for `indicatorCode` and `lifeCyclePhase`
**What is wrong:** Both are free `xs:string` properties. `GWP-total`, `GWP_total`, `gwp`, `GWP (total)` are all syntactically valid — semantically indistinguishable without a controlled vocabulary.
**Why it matters:** Without controlled vocabularies, the AAS data cannot be reliably processed by any automated system. Two EPDs using different indicator code conventions will appear to have different indicators.
**Change:** Add ConceptDescription `EPDIndicatorCode` and `EPDLifeCycleModule` ValueLists. Reference them from `indicatorCode` and `lifeCyclePhase` semanticIds.
**References:** EN 15804 Tables 1–3. EPD Int. non-construction indicator list `1709903284-indicators-default-list-version-2-240308.xlsx`.

---

### #6 — Refactor `representativenessReference` → `lcaMethodology` and remove ILCD artefacts
**What is wrong:** The section contains ILCD/openLCA database UUIDs (`referenceFlow.id`, `referenceFlow.amount`) and image path properties (`pictogramSource`, `flowDiagramSource`). It was introduced because the first instance was generated via an openEPD/openLCA intermediary. The section name has no normative EPD meaning.
**Why it matters:** ILCD artefacts expose internal LCA model identifiers to EPD data consumers. `referenceFlow.id` is a UUID meaningful only inside an openLCA database.
**Change:** Remove `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, `flowDiagramSource`, `dataSetValidUntil`. Rename section to `lcaMethodology`. Add structured `lcaSoftware`, `lcaDatabase`, `lciaMethod`, `allocationApproach`, `systemBoundaryType`.
**References:** EPD Int. GPI 5.0.1 §6. ISO 14044 §6.3.

---

### #7 — Add `productClassification [SML]`
**What is wrong:** No product classification is modelled. A downstream system cannot determine what type of product an EPD represents without reading the free-text description.
**Why it matters:** Every EPD platform uses product categories for routing, aggregation, and filtering. Digital Product Passport and ESPR specifically require product categorisation.
**Change:** Add `productClassifications [SML]` with `[classificationSystem, classCode, classVersion]` per entry.
**References:** EPD Int. GPI §4. PEP PCR scope. openEPD `product_classes` field. EU ESPR.

---

### #8 — Add `verificationType` and `verificationDate`
**What is wrong:** The verification section has a verifier identity and URL, but does not declare when verification occurred or what verification approach was used (Individual/PreVerifiedTool/ProcessCertification).
**Why it matters:** These are different assurance levels. A procurement system must know the verification type to assess EPD trustworthiness.
**Change:** Add `verificationType [Property, enum: IndividualVerification/PreVerifiedTool/ProcessCertification]` and `verificationDate [Property, xs:date]`.
**References:** EPD Int. GPI 5.0.1 §7. PEP PCR Ed.4 §4.3.

---

### #9 — Resolve all placeholder semantic IDs and fix the comma bug
**What is wrong:** 12+ semantic IDs use `http://example.com/` or `http://eclass.example.com/` placeholder URIs. `http://example.com/epd/lca,StandardsPcr` contains a literal comma — a URI parsing bug.
**Why it matters:** Placeholder URIs make the model machine-unresolvable. The comma bug may cause silent parsing failures in strict XML/JSON processors. A model claiming to use semantic IDs must have resolvable semantic IDs.
**Change:** Assign provisional `https://admin-shell.io/idta/EPD/...` URIs for all placeholder sections. Fix comma bug. Replace all `eclass.example.com` placeholders.
**References:** AAS Metamodel Part 1 V3.0 §7.2.3.

---

### #10 — Add multi-product / product variant architecture
**What is wrong:** A single `productArticleNumberOfManufacturer [Property]` cannot represent a product family. ODD-07 and ODD-22 defer this as "future work" — but the WAGO EPD itself covers a product family (221 Series) with an extrapolation table.
**Why it matters:** The majority of published EPDs in the electronics sector cover product families. The current model correctly handles at most the simplest EPD case.
**Change:** (a) Replace single article number with `productIds [SML]`. (b) Add `productType [enum]`. (c) Add optional `productVariants [SML]`. (d) Add optional `extrapolationFactors [SML]`.
**References:** PEP PCR Ed.4 §5.4. WAGO source extrapolation table. ODD-07, ODD-22.

---

*This review was produced as a first-session design review only. No changes to the AASX model or any source files were made. All findings are recommendations for working-group discussion and validation.*
