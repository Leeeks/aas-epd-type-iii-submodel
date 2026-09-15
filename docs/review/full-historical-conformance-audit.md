# Full Historical Conformance Audit

This document traces the conformance of the current EPD Type III Submodel implementation against the entire historical chain of source documents, review findings, and architecture decisions (ADRs).

## 1. Executive result

**CONFORMANT WITH MINOR OPEN ITEMS** (Following corrections made during this audit)

The model is structurally consistent with the final architectural decisions (ADR-01 through ADR-08) and the source requirements from PEP ecopassport and EPD International. All discovered implementation drifts were corrected. However, the issue of fabricated semantic identifiers remains an open item.

## 2. Source-to-model traceability matrix

| Concept | Source | Final decision | Current implementation | Status | Fix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Document identification** | EPD Int'l / PEP general info | Must be present to identify the EPD document. | `identificationPublication` correctly implements all identifying fields (`documentDomainId`, `documentIdentifier`, `documentIsPrimary`). | CONFORMANT | None |
| **Languages** | EPD publication formats | Represent available language versions of the declaration. | `identificationPublication/languages` is a repeatable `submodelElementList` populated with `DE`, `EN`, `FR`. | CONFORMANT | None |
| **verificationStatementUrl** | PEP / EPD Int'l Verification | ARCHITECTURAL SCOPE DECISION: An optional generic reference may be useful for some programs, but it was removed to streamline the model. | Completely removed from generic model, PUML, and `generate_wago_instance.py`. | CONFORMANT | Removed entirely during prior phase |
| **Product identity vs EPD scope** | Multi-product EPDs (ADR-04) | AAS represents the asset; EPD represents the scope. | `manufacturerProduct` correctly details the `221-422` asset; `EPDScope` correctly lists all 6 covered variants. | CONFORMANT | Typo in `21-422` mapping fixed to `221-422` |
| **Functional / Declared Unit** | ADR-07 / PCR | Distinct semantic concepts. Depending on the applicable PCR, one may be required, the other may be required, or both may appear. They are not universally mutually exclusive. | Both `DeclaredUnit` and `FunctionalUnit` exist in the model without enforcing technical mutual exclusivity. | CONFORMANT | None |
| **Lifecycle representation** | ADR-01 / ADR-02 | Must support specific and aggregated phases. Technical phase value preserved (e.g., `A1-A3`), `idShort` normalized to `stage_A1_A3`. | `DeclaredStages` correctly maps phases. `stageCode` stores `A1-A3`, `idShort` is `stage_A1_A3`. | CONFORMANT | Fixed script to use `A1-A3` value and dynamically generate `stage_A1_A3` idShort |
| **Environmental Results** | ADR-02 | Separate categories (Impact, Resource, Waste, Output). No monolithic LCIA list. | `EnvironmentalResults` SML categorizes 29 indicators, each with `resultCategory` and `stageValues`. | CONFORMANT | None |
| **Status semantics** | ADR-03 | Distinguish `Declared` 0.0 from `NotDeclared`. | Zeros correctly marked as `Declared` with value `0.0`. | CONFORMANT | Fixed leftover `"Measured"` fallback values to `"Declared"` |
| **Content Declaration** | ADR-06 / PEP | Must be optional for service EPDs; single biogenic carbon source. | `ContentDeclaration` is optional. Flat biogenic properties removed; nested structure used. | CONFORMANT | None |
| **LCA Methodology** | ADR-08 | Replace `representativenessReference` with `LCAMethodology`. | `LCAMethodology` fully implemented. Legacy fields (`referenceFlow`, `pictogramSource`) purged. | CONFORMANT | None |
| **Standards / PCR stack** | PEP PCR | Distinguish PCR, c-PCR, PSR, etc. | `lca_StandardsPcr` correctly separates `standardsCompliance` and `productCategoryRules`. | CONFORMANT | None |
| **EPD document packaging** | AASX spec | Embed PDF and image using valid package-relative URIs. | `epdDocument` and `productImage` correctly packaged in `aasx/files/` and validated. | CONFORMANT | None |

## 3. Legacy elements found
During the audit, the following legacy elements and implementation drifts were found:
- Minor typo in the WAGO example mapping JSON (`21-422` instead of `221-422`).
- Hardcoded `"Measured"` status in Python script fallbacks instead of `"Declared"` (violation of ADR-03).
- Outputting `"A1A3"` as the `stageCode` instead of the technical phase value `"A1-A3"` (violation of ADR-0002).

## 4. Missing implementation
None. The required concepts are all represented.

## 5. Incorrect implementation
None remaining. The implementation drifts (typo, `"Measured"` fallback, and `stageCode` hyphen preservation) were fixed.

## 6. Example-data completeness
The `wago-00001` example is highly complete:
- **Source-derived**: `documentIdentifier`, `declarationUrl`, `productName`, `coveredProductReferences`, `productMass`, Impact Indicators (e.g., GWP), Waste indicators, and the real publication language (`EN`).
- **Illustrative**: `FunctionalUnit` (explicitly marked), ResourceUse indicators (e.g., `PENRE`, `PERE`), Toxicity indicators, and additional languages (`DE`, `FR`). Note that illustrative values are not evidence that the real WAGO PEP contains those values.
- **Intentionally Empty**: None without explanation. All elements contain either source data or illustrative data to demonstrate the structure.

## 7. Packaged-file validation
The generation script inherently validates the packages:
- `ProductPicture_Wago_221_422.jpg` is properly embedded inside `aasx/files/`.
- `wago-00001-v01-01-en.pdf` is properly embedded and verified to have the correct length.
- Both use relative URIs in the XML model (e.g., `/aasx/files/...`).

## 8. Semantic-ID audit
An automated search across the template and instance `data.xml` confirmed that all placeholder `http://example.com/` and `http://eclass.example.com/` URIs have been replaced. However, the model still uses fabricated URIs that must not be presented as official:
- Valid ECLASS IRDIs (e.g., `0173-1#02-AAO676#003`)
- Fabricated provisional Working Group URIs (e.g., `https://wg-epd.example.com/draft/v1/...`) - This is still an `example.com` placeholder and not a genuinely controlled WG namespace.
- Fabricated provisional IDTA URIs (e.g., `https://admin-shell.io/idta/EPD/...`) - These are not officially allocated by IDTA.

## 9. Corrections implemented during audit
1. Fixed the SKU typo in `mapping.json` (`21-422` -> `221-422`).
2. Updated `generate_wago_instance.py` to preserve the technical phase name `A1-A3` as `stageCode` and dynamically generate `stage_A1_A3` as the `idShort`, conforming to ADR-0002.
3. Updated `generate_wago_instance.py` to correctly map missing or illustrative fallback indicators with `valueStatus = "Declared"`, conforming to ADR-03.
4. Regenerated the `wago-00001-v01-01-en-epd-submodel-instance.aasx` file.
5. Re-calculated `SHA256SUMS` for the updated example instance.

## 10. Remaining NEEDS DECISION items
- **Semantic Identifiers**: A genuinely controlled provisional project/WG namespace must be established, and fabricated `example.com` and `admin-shell.io` identifiers must be replaced.

## 11. PEP compatibility
Structurally compatible with the tested reference case. All required PEP core components (including nested Biogenic Carbon, Product/Packaging mass details, and specific PCR/PSR stack standards) can be represented.

## 12. EPD International non-construction compatibility
Structurally compatible with the tested reference case. The structure separates LCIA and LCI indicators properly and allows for missing or non-relevant modules to be documented through explicit `DeclaredStages` mapping rather than monolithic LCIA arrays.

## 13. EPD International construction compatibility
Structurally compatible with the tested reference case. The model easily accommodates the detailed A-D module breakdown required by EN 15804 and PCR 2019:14, properly tracing the indicators to specific stages.
