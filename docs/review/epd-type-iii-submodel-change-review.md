# Technical Review: EPD Type III Submodel Changes

**Date:** 2026-07-15
**Version:** 1.0
**Target Audience:** IDTA Working Group

## Purpose and scope
This document provides a technical review of the recent structural changes applied to the IDTA Submodel Template EPD Type III (Environmental Product Declaration). It is intended as a basis for decision-making and technical review by the working group. It focuses on the transition from hard-coded indicator structures to a generic, flexible IEC 61360-based structure, the normalization of identifiers, and the handling of characterization units.

## Reviewed artifacts
- `epd_smt_template_v3_v10.aasx` (Previous version)
- `epd_smt_template_v3_v12.aasx` (Current revised AASX template version)
- `WAGO-00001-V01.01-EN_AAS31.aasx` (Test instance populated with real PEP data)
- Scripts: `restructure_lcia_v11.py`, `generate_pep_aasx.py`

## Executive summary
The EPD Type III Submodel Template was fundamentally refactored to use a dynamic, template-based approach for LCIA results and resources instead of statically predefined indicator groups. Key improvements include dynamic `idShort` generation in instances for better tooling support (while keeping templates compliant with AASd-120), a refactored and cleaner `characterizationUnit` hierarchy, and successful validation against a real-world WAGO PEP. Several potential redundancies and missing fields were identified during the instantiation process, which are documented here for working group discussion.

## Overview of implemented changes

| Change ID | Affected path | Previous design | Current design | Rationale | Normative basis | Compatibility impact | Status | Review question |
|---|---|---|---|---|---|---|---|---|
| CHG-001 | `lciaResults/*` | Predefined static SubmodelElementCollections for each indicator group | Single generic template collection in SMT. Dynamic `idShort` (e.g. `GWP_total`) generated during instantiation. | Improves flexibility, reduces template bloat, enables dynamic addition of indicators. `idShort` improves Package Explorer UX. | AAS Part 1 V3.0 (AASd-120 restricts idShort in SML) | Breaking | Implemented | Do reviewers agree that idShort values for LCIA list entries shall only be assigned during instantiation and not fixed in the generic template? |
| CHG-002 | `*/lifeCyclePhaseValues/*` | Elements named "Unknown" in UI | Dynamic `idShort` (e.g., `A1_A3`) derived from `lifeCyclePhase` value. | Improves readability in AAS tools. | AAS Part 1 V3.0 | Minor | Implemented | Should `Total` remain an entry in `lifeCyclePhaseValues`, or should it be represented as a separate `totalValue` property? |
| CHG-003 | `*/characterizationUnit` | Flat or mixed structure | Nested structure: `unit`, `unitId`, optional `baseUnit` (`unit`, `unitId`). | Clearly separates the full LCIA unit from the physical base unit (e.g., ECLASS). | IEC 61360 | Breaking | Implemented | Do reviewers agree that the full LCIA characterization unit remains authoritative, while the ECLASS base unit is optional supplementary information? |
| CHG-004 | List semantics | Missing list semantics | `typeValueListElement` set to SMC. `semanticIdListElement` added in instance. | Formalizes list constraints. | AAS Part 1 V3.0 | Minor | Implemented | Are the applied list element semantics sufficient for standardizing the EPD structure? |

## Detailed change descriptions

### 1. idShort for LCIA results
- **Previous representation:** In older templates, or strictly standard V3 lists, elements without `idShort` are displayed as `Unknown` or generically (e.g., `SubmodelElementCollection`) in the AASX Package Explorer.
- **New representation:** Direct list elements of `lciaResults` in a concrete instance now receive an `idShort` derived from the `indicatorCode` (e.g., `indicatorCode: GWP-total` → `idShort: GWP_total`).
- **Normalization rules:** Spaces, dashes, and slashes are replaced by underscores. Non-alphanumeric characters are removed. Consecutive underscores are collapsed.
- **Conflict handling:** If an `idShort` conflict occurs (e.g., duplicate indicators), a suffix `_2` is appended.
- **Template vs. Instance:** In the generic template, the template entry has no `idShort` to comply with AAS V3 rule AASd-120 (direct children of a SubmodelElementList must not have an `idShort`). In the concrete instance, however, it is dynamically assigned to drastically improve UX in viewers like the AASX Package Explorer.
- **AAS Metamodel Impact:** AAS V3.0 restricts `idShort` usage in lists. Tools might flag this as a warning, but the UX benefit for human readability is significant.

### 2. idShort for Life Cycle Phases
- Analogous to LCIA results, `idShort` values are assigned to direct list elements of `lifeCyclePhaseValues` in the instantiated model.
- **Examples:** `A1-A3` → `A1_A3`, `B1-B7` → `B1_B7`, `C1-C4` → `C1_C4`, `D` → `D`, `Total` → `Total`.
- The actual normative value in the `lifeCyclePhase` property remains untouched (e.g., `A1-A3`). The `idShort` is strictly for unique identification within the model and better tool representation.

### 3. Modeling of Characterization Units
- **Compact Structure:** The structure was revised to cleanly separate the LCIA impact unit from the physical unit.
  ```text
  characterizationUnit
  ├── unit (e.g., "kg CO2 eq.")
  ├── unitId (e.g., "<controlled LCIA unit identifier>")
  └── baseUnit [optional]
      ├── unit (e.g., "kg")
      └── unitId (e.g., "0173-1#05-AAA731#005")
  ```
- `unit` designates the full LCIA characterization unit.
- `baseUnit` designates the physical base unit (e.g., from ECLASS). The ECLASS unit *does not* replace the LCIA unit; it is supplementary.
- `baseUnit` is strictly optional.
- Having identical child names (`unit`, `unitId`) is valid as they belong to different parent collections.
- Non-verified ECLASS units are not guessed. Custom LCIA `unitId` URIs are used as preliminary working identifiers until official IDTA/ECLASS IDs are confirmed.

### 4. Changes to Lists and Semantics
- **semanticIdListElement:** In the instance generation, a `semanticIdListElement` is explicitly injected into `lifeCyclePhaseValues` to formally define the semantics of the list items.
- **typeValueListElement:** Defined as `SubmodelElementCollection` for all generic lists to restrict list contents.
- **Cardinalities:** Kept flexible (`ZeroToMany`) for template definitions to allow arbitrary numbers of indicators in instances.
- **AAS Version:** Maintained at AAS V3.0. List semantics conform strictly to V3 specifications.

## Validation with the WAGO PEP
The dynamic model was tested against a real-world Product Environmental Profile (PEP): **WAGO-00001-V01.01-EN.pdf**.
- **Mapped Metadata:**
  - Registration Number: `WAGO-00001-V01.01-EN` (Version: `V01.01-EN`)
  - Dates: Issue Date (`02-2026`), Valid Until (`02-2031`), Validity Period (`5 years`)
  - Verifier Accreditation: `VH44`
  - PCR Reference: `PCR-4-ed4-EN-2021 09 06`
  - Product Data: `221 Series / Splicing Connector with Levers`, Reference `221-422`, Flow `1.958 g`, Service Life `30 years`.
- **Mapped Indicators:** 20 LCIA indicators, 10 Resource Use indicators, 3 Waste categories, 4 Output flows.
- **Life Cycle Phases:** Successfully mapped values for phases `A1-A3` (aggregated), `A4`, `A5`, `B1-B7` (aggregated), `C1-C4` (aggregated), and `D`.
- **Value Handling:** Negative values (e.g., carbon sequestration) and scientific notation values were correctly processed and retained as `xs:decimal`.
- **Conclusion:** The instance (`WAGO-00001-V01.01-EN_AAS31.aasx`) serves as a practical proof of concept that the restructured, generic SMT can successfully and robustly handle complex, real-world EPD data.

## Potential redundancies
| Affected Elements (AAS Path) | Overlap Explanation | Recommendation | Compatibility Impact | Status |
|---|---|---|---|---|
| `epdId` vs `registrationId` | Both fields frequently store the exact same PEP/EPD registration number. | Merge / Clarify definitions | Minor | Proposed |
| Declared Unit Modeling | Declared unit is often implicitly defined in metadata and explicitly in `referenceUnitForCalculation`. | Clarify primary source of truth | None | Open for decision |
| `kgPerDeclaredUnit` vs `massPerDeclaredUnit` | Both describe the mass of the declared unit. | Merge / Rename to `massPerDeclaredUnit` | Breaking | Proposed |
| `productServiceLifeYears` vs `referenceServiceLife` | Both specify the service life. Often identical data. | Merge to `referenceServiceLife` | Breaking | Proposed |
| Reference Flow vs Declared Unit | Reference flow and declared unit are often synonymous in PEPs but modeled in parallel. | Retain, but add clear guidance | None | Open for decision |

## Information not yet represented
The following information fields from the WAGO PEP currently lack a standardized, dedicated property in the model:
- Structured functional unit (currently mapped as plain text)
- Separate product mass and packaging mass (currently only total/reference flow)
- Detailed material composition
- Product families and covered variants
- Indicator- and phase-specific extrapolation factors
- Verifier accreditation number (`VH44`) - mapped, but needs formal review for correct placement
- Structured information on LCA software, background database, and LCIA method
- Status of individual modules (e.g., distinguishing between `declared`, `not applicable`, `excluded`, `aggregated`)

*Note: These are documented as review findings; no template changes were made for these items yet.*

## Backward compatibility and migration impact
- **Breaking Changes:** Moving from static indicator collections to a single generic list (`lciaResults`) is a breaking structural change. Existing parsers expecting hard-coded paths (e.g., `lciaResults/GWP-total`) will fail.
- **Migration Path:** Software extracting EPD data must be updated to iterate over `lciaResults` lists and dynamically check the `indicatorCode` property instead of relying on the structural `idShort`.
- **AAS Version:** Retained V3.0.

## Validation results
- [x] AASX file can be opened.
- [x] File can be saved and reopened without corruption.
- [x] `idShort` values in the instance are successfully retained.
- [x] LCIA indicators are no longer displayed as `Unknown` in the Package Explorer.
- [x] Life cycle phases are no longer displayed as `Unknown`.
- [x] Numeric values, signs (including negatives), and units are fully retained.
- [x] `semanticIdListElement` and list element semantics are structurally consistent.
- [x] Template (generic) and Instance (specific) architectures are clearly separated.
- [x] Known tool warnings (e.g., `idShort` in Lists) are distinguished from actual schema failures.
- [x] AAS version explicitly maintained at 3.0.

*No formal conformance to XML schemas is asserted here, as AASd-120 warnings are expected when `idShort` is used in lists. This was a conscious decision to improve UX.*

## Open decisions for the working group
1. **List IDShorts:** Do we formally accept the addition of `idShort` to List elements in *instances* to improve UI representation, despite AASd-120?
2. **Characterization Units:** Is the `baseUnit` approach sufficient, and do we agree to use preliminary URIs for LCIA units until ECLASS provides them?
3. **Total Values:** Should `Total` be handled as just another phase in `lifeCyclePhaseValues`, or separated as a distinct property to prevent aggregation errors?
4. **Redundancies:** Which of the identified potential redundancies (`epdId` vs `registrationId`, etc.) should be merged in the next template release?

## Reviewer comment table
(Please see the accompanying `EPD_Type_III_Submodel_Review_Comments.xlsx` for submitting feedback.)

| Comment ID | Reviewer | Section / Change ID | Comment | Proposed resolution | Decision | Status |
|---|---|---|---|---|---|---|
| C-001 | | CHG-001 | | | | |
| C-002 | | CHG-003 | | | | |

## Change log
- **2026-07-15**: Initial draft of structural changes for review. Validated against WAGO PEP.

## Appendix: before/after structures
**Before (Static, hardcoded):**
```text
lciaResults (SubmodelElementCollection)
├── GWP_total (SubmodelElementCollection)
│   ├── indicatorCode: "GWP-total"
│   └── lifeCyclePhaseValues
│       ├── (Unknown SMC) -> lifeCyclePhase: "A1-A3", value: 1.2
└── ODP (SubmodelElementCollection)
    └── ...
```

**After (Generic List with dynamic instantiation):**
```text
lciaResults (SubmodelElementList)
├── GWP_total (SubmodelElementCollection) [In Instance Only]
│   ├── indicatorCode: "GWP-total"
│   ├── characterizationUnit
│   │   ├── unit: "kg CO2 eq."
│   │   └── baseUnit (optional)
│   └── lifeCyclePhaseValues (SubmodelElementList)
│       ├── A1_A3 (SubmodelElementCollection) [In Instance Only]
│       │   ├── lifeCyclePhase: "A1-A3"
│       │   └── value: 1.2
```
