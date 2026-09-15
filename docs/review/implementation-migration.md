# EPD Submodel Architecture Refactoring Migration Guide

## Overview

This guide details the structural changes made to the AAS EPD Type III Submodel template to align with the new model semantics and to resolve architectural issues outlined in the Architecture Decision Records (ADRs).

## Key Structural Changes

### 1. System Boundaries and LCAMethodology
- **Removed**: The root-level `systemBoundary` SubmodelElementCollection (and its boolean flags like `includesA1_A3`).
- **Removed**: The `representativenessReference` collection.
- **Added**: `LCAMethodology` [SMC] which absorbs legitimate methodological parameters (e.g. reference year).
- **Added**: `DeclaredStages` [SML] inside `LCAMethodology`, containing a list of `StageDeclaration` [SMC] elements. Each specifies the `stageCode` and `stageStatus` (e.g., Assessed, NotAssessed).

### 2. Environmental Results
- **Removed**: `lciaResults` [SML].
- **Added**: `EnvironmentalResults` [SML], designed to house all indicator types in a unified schema structure.
- **Added**: Inside `EnvironmentalResults`, `EnvironmentalResult` [SMC] specifies the `resultCategory` (e.g., `ImpactIndicator`, `ResourceUse`, `Waste`, `OutputFlow`), `indicatorCode`, and a nested `stageValues` list.
- **Impact on Mapping**: Tools must map original results to `EnvironmentalResult` by explicitly categorizing the indicator. 

### 3. EPD Scope Definition
- **Added**: `EPDScope` [SMC] at the root level.
- **Added**: `scopeType` (Instance, Type, Family), `coveredProductReferences`, and `scopeDescription` provide explicit context for what the environmental impacts apply to, resolving the single vs. family representation ambiguity.

### 4. Content Declaration
- **Added**: `ContentDeclaration` [SMC] provides LCA-relevant summary metrics (`productMass`, `recycledContentPercentage`, `biogenicCarbonContentProduct`) decoupled from the general manufacturer BOM, supporting specific end-of-life calculations.

### 5. Reference Units Unified
- **Modified**: Both `DeclaredUnit` and `FunctionalUnit` now use a standard sub-structure requiring `quantity` (xs:decimal) and `unit` (xs:string), ensuring numeric parsability instead of arbitrary string descriptions.

### 6. Semantic Identifier Draft Namespace
- **Modified**: Elements lacking official ECLASS or IDTA semantic identifiers have been migrated from placeholder domains (e.g. `example.com`) to the provisional `https://wg-epd.example.com/draft/v1/` namespace to explicitly flag them for future standardization.

## Example Migration

The included WAGO PEP example (`examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx`) has been fully migrated to demonstrate compliance with this new structure, effectively separating the semantic meaning of the results from the constraints of the PEP document structure.

---

## Review Corrections (2026-09-15)

### 7. DeclaredUnit Duplicate Cleanup

**Background**: Inspection of the AASX packages revealed three distinct occurrences of the declared-unit concept:

| # | Location | idShort | SemanticId | Action |
|---|----------|---------|------------|--------|
| A | Submodel root level (top-level SMC) | `declaredUnit` (camelCase) | `https://admin-shell.io/idta/EPD/DeclaredUnit/1/0` | **Removed** |
| B | Inside `manufacturerProduct` value list | `declaredUnit` (camelCase) | `https://admin-shell.io/idta/EPD/DeclaredUnit/1/0` | **Removed** |
| C | Submodel root (after FunctionalUnit) | `DeclaredUnit` (PascalCase) | `https://wg-epd.example.com/draft/v1/DeclaredUnit` | **Kept — canonical** |

The legacy entries (A and B) used the old IDTA semId and contained redundant children
(`declaredQuantity`, `unitOfMeasure`, `massPerDeclaredUnit`, `referenceServiceLife`)
that conflated product-level attributes with the reference-unit definition.

**Removed ConceptDescriptions**:
- `https://admin-shell.io/idta/EPD/DeclaredUnit/1/0`
- `http://eclass.example.com/declaredUnit.qty`
- `http://eclass.example.com/declaredUnit.unit`
- `http://eclass.example.com/kgPerDeclaredUnit.qty`
- `http://eclass.example.com/kgCPerDeclaredUnit.qty`
- `http://eclass.example.com/kgCBiogenicPerDeclaredUnit.qty`

**Canonical DeclaredUnit** (idShort=`DeclaredUnit`, PascalCase) now has:
- `quantity` (xs:decimal) — e.g. `1`
- `unit` (xs:string) — e.g. `item`
- `description` (MLP) — human-readable mass/packaging note

`massPerDeclaredUnit` is retained as a standalone property inside `manufacturerProduct`
as a numeric conversion factor (kg per declared unit) for traceability to the source
EPD declaration document.

**Tooling**: `scripts/patch_template_aasx.py` applies the cleanup idempotently to the
template AASX; `scripts/generate_wago_instance.py` applies it during instance generation.

### 8. EnvironmentalResults stageValues Population

All 29 `EnvironmentalResult` entries in the WAGO example have been populated with
`StageValue` children (415 StageValue SMCs total):

- **12 impact indicators** (GWP-total/fossil/biogenic/luluc, ODP, AP, EP-fw/m/t, POCP,
  ADPF, ADPE): values sourced from PEP ecopassport mapping JSON (EF 3.0 characterisation).
- **8 illustrative impact indicators** (WDP, Total\_PE, PM, IR, ETP\_fw, HTP\_c, HTP\_nc,
  SQP): clearly labelled `[ILLUSTRATIVE EXAMPLE]` — not in PEP source data.
- **7 output/waste flows** (HWD, NHWD, RWD, CRU, MFR, MER, EE): sourced from mapping JSON.
- **2 illustrative ResourceUse** indicators (PENRE, PERE): added as examples since
  `resource_uses` is empty in the PEP source.

Stage status semantics (per ADR-03):
- `Measured` — value declared in source, including zero values
- `NotDeclared` — stage is `null` in source (C1–C4 for all indicators)

### 9. Product Image Embedded

`ProductPicture_Wago_221_422.jpg` is now packaged inside the WAGO AASX at
`/aasx/files/ProductPicture_Wago_221_422.jpg`.
The `productImage` File element references this path with `contentType=image/jpeg`.

### 10. Full-Field Population

All previously empty fields in the WAGO example have been populated including:
`manufacturerName`, `productName`, `manufacturingSites`, `manufacturingDescription`,
`applicableJurisdictions`, `biogenicCarbonContent` (decimal type fixed),
`DeclaredStages` (all 15 stage codes with Assessed/NotAssessed status),
`programOperator`, `thirdPartyVerifier`, `epdDeveloper`, `verificationType`,
`FunctionalUnit` (illustrative), `EPDScope`, `ContentDeclaration`.

### 11. Comprehensive Semantic and Packaging Corrections (2026-09-15)

Following a comprehensive 16-point review, the model and WAGO instance were updated to resolve semantic ambiguities and fix packaging errors:

- **Document Identification**: `documentIds` now explicitly defines the identifier domain. 
  - `documentDomainId` = `PEP ecopassport`
  - `documentIdentifier` = `WAGO-00001-V01.01-EN` (the actual PEP document ID)
  - `documentIsPrimary` = `true`
- **Languages**: The `languages` SML now demonstrates repeatable properties with ISO 639-1 language codes (DE, EN, FR) to indicate the languages the EPD is available in. (Note: DE and FR are illustrative for the WAGO instance).
- **Declaration URL**: `declarationUrl` is populated with the public PEP ecopassport link. `verificationStatementUrl` is kept empty as it's optional and the statement is not public. Redundant `sourceDeclarationReference` from `EPDScope` was completely removed.
- **Legacy ILCD Fields Removed**: `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, and `flowDiagramSource` have been purged from `LCAMethodology` and the template concept descriptions, as they were legacy ILCD/LCA software artifacts without generic downstream meaning.
- **Methodology Context**: 
  - `energyModel` populated with geographic scenario `DE`.
  - `standardsCompliance` now contains a list including `ISO 14025` and `EN 15804`.
  - `productCategoryRules` contains a list representing the PCR stack (e.g. `PCR-ed4-EN-2021 09 06`, `PEP-PCR-ed3-EN-2015 04 02`).
- **Product Scope**: `productName` is explicitly set to the family name ("221 Series / Splicing Connector with Levers"). `productArticleNumberOfManufacturer` is the specific variant ("221-422"). `coveredProductReferences` now includes an array of all covered WAGO 221 variants (`221-412`, `221-413`, `221-415`, `221-422`, `221-423`, `221-425`).
- **Result Status Semantics**: Changed stage value status from the inappropriate "Measured" to "Declared" for existing numeric values, while maintaining "NotDeclared" for nulls.
- **Biogenic Carbon Deduplication**: The `biogenicCarbonContent` SubmodelElementCollection was completely removed from `manufacturerProduct` and moved to `ContentDeclaration`. Flat properties `biogenicCarbonContentProduct` and `biogenicCarbonContentPackaging` were removed, establishing the nested SMC as the single canonical source of truth.
- **EPD Document AASX Packaging Fix**: Fixed the `epdDocument` `File` element which previously triggered AASX Package Explorer errors. The generator script now extracts the source `wago-00001-v01-01-en.pdf`, correctly packages it into the AASX ZIP under `/aasx/files/wago-00001-v01-01-en.pdf`, and references it properly with `application/pdf`.
