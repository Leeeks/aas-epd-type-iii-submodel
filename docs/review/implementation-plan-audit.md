# Implementation Plan Audit

This document is the final audit report of the EPD Type III Submodel implementation branch against the agreed-upon 16-point review plan.

## Audit Table

| Planned item | Repository location | Status | Evidence | Required fix |
|--------------|---------------------|--------|----------|--------------|
| **Document identification** | `scripts/generate_wago_instance.py` | IMPLEMENTED | `documentDomainId` is set to `PEP ecopassport`. `documentIdentifier` is set to `WAGO-00001-V01.01-EN`. `documentIsPrimary` is `true`. | None |
| **Languages** | `scripts/generate_wago_instance.py` | IMPLEMENTED | `languages` SML is populated with repeatable properties: `DE`, `EN`, `FR`. | None |
| **declarationUrl** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Populated with the public PEP ecopassport URL. | None |
| **verificationStatementUrl** | `model/template/epd-type-iii-submodel-template.aasx`, `model/epd-type-iii-model.puml` | IMPLEMENTED | The property and its ConceptDescription have been entirely removed from the generic model template, the PUML diagram, and the generator script, as the statements are not public. | None (Fixed during audit) |
| **Product identity** | `scripts/generate_wago_instance.py` | IMPLEMENTED | `productName` is explicitly set to the family name; `productArticleNumberOfManufacturer` is set to the specific article `221-422`. | None |
| **Legacy ILCD/openLCA artefacts** | `model/template/epd-type-iii-submodel-template.aasx` | IMPLEMENTED | `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, and `flowDiagramSource` have been successfully purged from `LCAMethodology` and the template concept descriptions. Orphaned PUML/SVG files were also removed. | None (Fixed during audit) |
| **energyModel** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Meaningful geographic scenario example (`DE`) is populated. | None |
| **standardsCompliance** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Populated with representative ISO 14025 and EN 15804 entries. | None |
| **productCategoryRules** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Populated with PCR and PEP-PCR stack entries. | None |
| **epdDocument** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Script correctly copies the PDF into `/aasx/files/wago-00001-v01-01-en.pdf`, references it as `application/pdf`, and validates the non-empty file inside the zip. | None |
| **valueStatus** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Values changed from the inappropriate "Measured" to "Declared", while nulls correctly remain "NotDeclared". Numeric zeros remain numeric zero. | None |
| **coveredProductReferences** | `scripts/generate_wago_instance.py` | IMPLEMENTED | All 6 WAGO 221 variants from the source EPD are populated. | None |
| **sourceDeclarationReference** | `model/template/epd-type-iii-submodel-template.aasx` | IMPLEMENTED | Removed completely from `EPDScope` to avoid redundancy with `declarationUrl`. | None |
| **Biogenic carbon** | `model/template/epd-type-iii-submodel-template.aasx` | IMPLEMENTED | Flat duplicates were removed, establishing the nested `biogenicCarbonContent` collection in `ContentDeclaration` as canonical. | None |
| **DeclaredUnit** | `model/template/epd-type-iii-submodel-template.aasx` | IMPLEMENTED | Legacy duplicates removed, retaining only the single canonical representation. | None |
| **EnvironmentalResults / stageValues** | `scripts/generate_wago_instance.py` | IMPLEMENTED | Fully populated with 415 StageValue SMCs across ImpactIndicators, ResourceUse, Waste, and OutputFlows. | None |
| **Product picture** | `scripts/generate_wago_instance.py` | IMPLEMENTED | The image `ProductPicture_Wago_221_422.jpg` is successfully packaged in the AASX and verified in the automated check. | None |
| **Example completeness** | `scripts/generate_wago_instance.py` | IMPLEMENTED | All fields contain real source-derived values or well-documented illustrative placeholders (e.g. FunctionalUnit). | None |

## Fully implemented items
All 18 audited points have been fully implemented. 

## Corrected during this audit
- **`verificationStatementUrl`**: Removed from the AASX template, the `patch_template_aasx.py` script, and the `epd-type-iii-model.puml` diagram.
- **Orphaned Legacy Documentation**: Deleted orphaned `representativenessReference.puml` and `.svg` files that were left over from earlier template cleanups.
- **AASX Hashes**: `SHA256SUMS` updated to reflect the cleaned template and instance.

## Remaining intentional deviations
None.

## Removed model elements
- `verificationStatementUrl`
- `referenceFlow.id`
- `referenceFlow.amount`
- `pictogramSource`
- `flowDiagramSource`
- `sourceDeclarationReference`
- `biogenicCarbonContentProduct`
- `biogenicCarbonContentPackaging`

## Files changed
- `scripts/patch_template_aasx.py`
- `model/template/epd-type-iii-submodel-template.aasx`
- `docs/model/epd-type-iii-model.puml`
- `docs/model/epd-type-iii-model.svg`
- `docs/model/sections/programOperatorVerification.svg`
- `examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx`
- `validation/SHA256SUMS`

*Deleted files:*
- `docs/model/sections/representativenessReference.puml`
- `docs/model/sections/representativenessReference.svg`

## Validation results
The generator script (`scripts/generate_wago_instance.py`) ran successfully, verifying the correct packaging of the PDF and product image, the absence of legacy `declaredUnit` concepts, and the exact count of 29 `EnvironmentalResult` indicators with 415 `StageValue` SMCs.

## Final recommendation
**IMPLEMENTATION MATCHES PLAN**

The generated AASX template and the instantiated WAGO example now fully reflect the audited and agreed-upon structural modifications. No remaining deviations exist.
