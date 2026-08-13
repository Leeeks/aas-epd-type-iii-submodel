# Open Design Decisions

## Decision ID: ODD-01
**Topic**: Final AAS metamodel version
**Current state**: Generated for V3.0
**Options**: Keep V3.0 or wait for newer Minor/Major Releases.
**Preferred proposal**: Keep V3.0
**Compatibility impact**: Toolchain dependency
**Required reviewers**: AAS experts
**Status**: open

## Decision ID: ODD-02
**Topic**: Use of idShort for direct list elements
**Current state**: idShorts are generated
**Options**: Check V3.0 model specifications.
**Preferred proposal**: Remove idShort if lists strictly forbid it according to the schema.
**Compatibility impact**: SubmodelElementList conformity
**Required reviewers**: AAS Architect
**Status**: open

## Decision ID: ODD-03
**Topic**: Handling of Total in life cycle phases
**Current state**: Modeled as `Total`.
**Options**: Own indicator or special phase.
**Preferred proposal**: Keep `Total` as a life cycle phase.
**Compatibility impact**: Mapping effort
**Required reviewers**: LCA experts
**Status**: proposed

## Decision ID: ODD-04
**Topic**: Final LCIA unit IDs and namespace
**Current state**: Working IDs partially used.
**Options**: Coordination with ECLASS for missing units.
**Preferred proposal**: Define a namespace for missing LCIA units until ECLASS officially lists them.
**Compatibility impact**: Reference resolution
**Required reviewers**: IDTA working group
**Status**: open

## Decision ID: ODD-05
**Topic**: Use of ECLASS base units
**Current state**: Optionally included as `baseUnit`.
**Options**: Remove vs. make mandatory.
**Preferred proposal**: Leave optional, as ECLASS base units do not replace the full LCIA unit (e.g., kg CO2-eq).
**Compatibility impact**: High
**Required reviewers**: LCA experts
**Status**: proposed

## Decision ID: ODD-06
**Topic**: Structured functional unit & masses
**Current state**: Separated product and packaging mass as well as material composition partially mapped.
**Options**: Expand detailing.
**Preferred proposal**: Focus on simple weight specifications in the EPD scope.
**Compatibility impact**: Low
**Required reviewers**: LCA experts
**Status**: open

## Decision ID: ODD-07
**Topic**: Product families and variants, extrapolation factors
**Current state**: Not yet modeled deeply.
**Options**: Introduce references or multiplication factors.
**Preferred proposal**: For now, restrict to generic EPDs without complex formulas.
**Compatibility impact**: High
**Required reviewers**: LCA experts
**Status**: deferred

## Decision ID: ODD-08
**Topic**: Verifier accreditation number
**Current state**: Partially included.
**Options**: Enforce as a separate field in Verification.
**Preferred proposal**: Extend by a specific property.
**Compatibility impact**: Medium
**Required reviewers**: IDTA working group
**Status**: open

## Decision ID: ODD-09
**Topic**: Structured LCA software and database information
**Current state**: Available as a text field.
**Options**: Split into Tool, Version, DB, DB Version.
**Preferred proposal**: Split.
**Compatibility impact**: High
**Required reviewers**: LCA experts
**Status**: open

## Decision ID: ODD-10
**Topic**: Module status (declared, notApplicable, excluded, aggregated)
**Current state**: Implicitly handled via missing values or flags.
**Options**: Introduce explicit status property for modules.
**Preferred proposal**: Enum-based status property.
**Compatibility impact**: High
**Required reviewers**: LCA experts
**Status**: open

## Decision ID: ODD-11
**Topic**: Possible redundant properties
**Current state**: Some overlaps with Nameplate.
**Options**: Clean up and reference.
**Preferred proposal**: Clean up.
**Compatibility impact**: High
**Required reviewers**: AAS Architect
**Status**: proposed

## Decision ID: ODD-12
**Topic**: Final Semantic IDs and placeholder IDs
**Current state**: Some placeholders (e.g., 0173-1#...) present.
**Options**: Wait for official registration.
**Preferred proposal**: Continue to use working IDs until release.
**Compatibility impact**: Medium
**Required reviewers**: IDTA working group
**Status**: open

## Decision ID: ODD-13
**Topic**: Licensing of artifacts
**Current state**: Unclarified (see LICENSE_DECISION_REQUIRED.md).
**Options**: Apache 2.0, MIT, or proprietary/IDTA-specific.
**Preferred proposal**: Apache 2.0 for models.
**Compatibility impact**: None
**Required reviewers**: IDTA Legal
**Status**: open

## Decision ID: ODD-14
**Topic**: Publication of the WAGO PEP in the repository
**Current state**: WAGO-00001-V01.01-EN.pdf is included.
**Options**: Keep or set a link.
**Preferred proposal**: Keep, provided WAGO agrees.
**Compatibility impact**: None
**Required reviewers**: WAGO representatives
**Status**: open

## Decision ID: ODD-15
**Topic**: Indicator-specific quantitative ConceptDescriptions for LCIA result values
**Status**: proposition – open for working-group discussion. **NOT implemented.**

### Problem statement

The current generic model assigns all LCIA numeric values the same generic semantic:

```
value
  semanticId → LifeCyclePhaseValue
  valueType  → xs:decimal
  value      → 0.0124
```

This value cannot be interpreted completely in isolation. A consumer must inspect the surrounding `LCIAResultEntry` to determine `indicatorCode` and `characterizationUnit`. The individual numeric property does not carry indicator-specific quantitative semantics and cannot reference a unit directly via its ConceptDescription.

Structurally, the generic model is valid and enables an extensible LCIA architecture, but the IEC 61360 `REAL_MEASURE` data type (which requires a unit) cannot be applied to the generic `LifeCyclePhaseValue` ConceptDescription. This is the reason `dataType` has been left unspecified on `LifeCyclePhaseValue` as an interim correction (see CHANGELOG).

### Proposed long-term solution

Introduce **indicator-specific quantitative ConceptDescriptions**, while preserving the generic LCIA structural pattern.

Each supported LCIA indicator would receive its own result-value ConceptDescription:

```
GWP_total_ResultValue
  preferredName : "Global warming potential – total result value"
  dataType      : REAL_MEASURE
  unit          : kg CO2-eq
  isCaseOf      → LifeCyclePhaseValue

AP_ResultValue
  dataType      : REAL_MEASURE
  unit          : mol H+-eq
  isCaseOf      → LifeCyclePhaseValue

ODP_ResultValue
  dataType      : REAL_MEASURE
  unit          : kg CFC11-eq
  isCaseOf      → LifeCyclePhaseValue

PENRT_ResultValue
  dataType      : REAL_MEASURE
  unit          : MJ
  isCaseOf      → LifeCyclePhaseValue
```

The actual value property in an LCIA result entry would then reference the indicator-specific ConceptDescription:

```
value
  semanticId → GWP_total_ResultValue
  valueType  → xs:decimal
  value      → 0.0124
```

### Motivation / advantages

- Each quantitative LCIA value becomes semantically interpretable on its own.
- `REAL_MEASURE` can be used correctly, together with the correct characterization unit.
- The generic `LifeCyclePhaseValue` concept still serves as the common semantic abstraction.
- `isCaseOf` expresses the relationship between generic and indicator-specific concepts.
- Generic consumers can continue to reason about `LifeCyclePhaseValue`.
- More specific consumers can distinguish GWP, AP, ODP, etc. directly from the value property's `semanticId`.
- IEC 61360 semantics are used more explicitly and completely.

### Trade-offs and open questions requiring working-group discussion

- A separate quantitative ConceptDescription is required for every supported LCIA indicator.
- This substantially increases the number of ConceptDescriptions.
- The relationship between the existing indicator enumeration ConceptDescriptions (used as `ValueList` values for `indicatorCode`) and the new quantitative result ConceptDescriptions must be clearly defined and kept non-overlapping.
- Naming conventions and semantic ID patterns need a consistent, agreed-upon scheme.
- It must be decided whether `isCaseOf` is the appropriate AAS relation, or whether another semantic modelling pattern is preferred by IDTA.
- Existing AAS tooling and semantic matching behaviour with `isCaseOf` should be verified.
- Extension with future EPD/LCIA indicators must remain straightforward.
- Backwards compatibility with existing instances and parser complexity should be considered.

### Current interim solution (implemented)

Pending working-group discussion, the chosen interim approach remains:

```
generic LifeCyclePhaseValue ConceptDescription
  preferredName : "Life cycle phase value"
  definition    : "Numeric LCIA value for the declared life cycle module."
  dataType      : <not specified>
  unit          : <not specified>

value Property
  semanticId → LifeCyclePhaseValue
  valueType  → xs:decimal
  value      → <numeric>
```

The applicable unit is resolved from `characterizationUnit` in the enclosing `LCIAResultEntry`.

**Compatibility impact**: High (if implemented – would require new semantic IDs and migration of all existing instances)
**Required reviewers**: IDTA working group, LCA experts, AAS Architect

## Decision ID: ODD-16
**Topic**: EPD Publication / Lifecycle Status vs. Technical Access Control
**Status**: OPEN / PROPOSITION – Not implemented

### Problem statement

The previous draft included a boolean `private` property originating from openEPD transport schemas. This field combined access control, workflow status, and publication visibility into a single EPD domain property.

### Distinction of concerns

1. **Publication / Workflow Lifecycle Status**:
   Describes the editorial and legal lifecycle stage of an EPD record, for example:
   - `Draft`: EPD creation in progress, unverified.
   - `InReview`: Under verification by a third-party verifier or Program Operator.
   - `Released`: Officially published and valid.
   - `Withdrawn`: Retracted by the manufacturer or Program Operator prior to expiration.
   - `Expired`: Past its validity period (`validUntil`).

2. **Technical Access Control / Authorization**:
   Determines which clients/users can read or modify the Submodel instance (e.g., public vs. internal network, role-based access). This is an infrastructure concern handled by standard AAS Access Control (ABAC/RBAC) mechanisms, not domain properties inside the Submodel.

### Proposition

Remove `private` from core domain data (implemented). If working-group consensus requires representing incomplete/draft EPD records, introduce a dedicated `publicationStatus` property with a controlled enumeration (`Draft`, `InReview`, `Released`, `Withdrawn`, `Expired`), kept strictly separate from AAS access control security policies.

**Compatibility impact**: Low
**Required reviewers**: IDTA working group, Program Operators, AAS Security WG

## Decision ID: ODD-17
**Topic**: Incomplete Date Precision and Duration-Based Validity
**Status**: OPEN / PROPOSITION

### Problem statement

Program Operators (e.g., PEP ecopassport) frequently publish EPDs with issue dates specifying only Month and Year (e.g., `02-2026`) and define validity as a period (e.g., "5 years", giving validity until `02-2031`).

`dateOfIssue` and `validUntil` use `valueType = xs:date` in the AAS model, which requires complete `YYYY-MM-DD` ISO calendar dates. In previous drafts, strings like `"02-2026"` were stored directly under `xs:date`, causing XSD validation failures.

### Options for Working-Group Resolution

1. **Normative Day Derivation Rule**: Define a normative rule that when a Program Operator specifies Month/Year `YYYY-MM`, `dateOfIssue` defaults to the 1st day of the month (`YYYY-MM-01`) and `validUntil` defaults to the last day of the month.
2. **Flexible Date Datatype**: Allow `dateOfIssue` and `validUntil` to use `xs:string` or `xs:date` / `xs:gYearMonth` depending on source precision.
3. **Explicit Precision Qualifier**: Add a metadata qualifier describing date precision (e.g. `Day`, `Month`, `Year`).

Inventing a calendar day without a normative rule is unacceptable. Until the working group defines a standard convention, exact dates should be used where available, and date precision handling remains an open design topic.

**Compatibility impact**: Medium
**Required reviewers**: IDTA working group, Program Operators

## Decision ID: ODD-18
**Topic**: Placement of Source Provenance Metadata (`sourceDataFormat`)
**Status**: OPEN / PROPOSITION

### Problem statement

The property `sourceDataFormat` (renamed from `originalDataFormat`) describes the original format or representation from which the AAS EPD submodel instance was generated (e.g., `openEPD`, `ILCD+EPD`, `PEP XML`, `PEP Ecopassport PDF`, `manual`).

Currently, `sourceDataFormat` is located inside `identificationPublication`.

### Proposition

Evaluate whether `sourceDataFormat` should remain an optional property within `identificationPublication`, or whether it should be moved to a dedicated AAS provenance/source-information section if IDTA standardizes submodel-level provenance metadata across Submodel Templates.

**Compatibility impact**: Low
**Required reviewers**: IDTA working group, AAS Architecture WG

## Decision ID: ODD-19
**Topic**: Adoption of IDTA ContactInformation for EPD organizations
**Status**: PARTIALLY IMPLEMENTED

### Problem statement

The previous draft modeled `programOperator`, `thirdPartyVerifier`, and `epdDeveloper` as partially structured SMCs with redundant flat properties (e.g., `thirdPartyVerifier.name`, `programOperator.id`) and non-standard properties like `RoleOfContactPerson`. This led to semantic ambiguities and duplicated structures.

### Proposition

Refactor these organizational elements to use the established IDTA `ContactInformation` semantics (e.g. `https://admin-shell.io/idta/ContactInformation/1/0/ContactInformation`).
- Flat fields like `name` and `email` are replaced by standard `ContactInformation` properties such as `Company` and the `EmailAddress` SMC.
- The obsolete `RoleOfContactPerson` and flat properties are removed.
- `programOperator` cardinality is updated to 1.

### Implementation status

- **`programOperator`**: Implemented (commit `771057f`). Uses IDTA ContactInformation semanticId; `Company` property (xs:string, `ZeroToMany`) present. Note: SME type is `property`, not `multiLanguageProperty` as required by IDTA 02002. Deferred to future cleanup.
- **`thirdPartyVerifier`**: Implemented (commit `771057f`). Uses IDTA ContactInformation semanticId; extended with EPD-specific `verifierAccreditationId` and `verificationStatementUrl`.
- **`epdDeveloper`**: **Implemented** (this change). `Company` added as `multiLanguageProperty` with authoritative semantic ID `0173-1#02-AAW001#001`, cardinality `One`. Custom `epdDeveloper.name` CD removed. `RoleOfContactPerson` (wrong-IRDI) CD removed.

### Semantic-ID mismatch found and reported

The ConceptDescription previously associated with `RoleOfContactPerson` used IRDI `0173-1#02-AAQ836#005`. This IRDI belongs to the IDTA 02002 **Email** SubmodelElementCollection, not to `RoleOfContactPerson`. The authoritative IRDI for `RoleOfContactPerson` is `0173-1#02-AAO204#003`. Since `RoleOfContactPerson` has been removed from `epdDeveloper`, the CD with the wrong IRDI was removed without correction.

**Compatibility impact**: High (requires structural update of AAS instances)
**Required reviewers**: IDTA working group, AAS Architect

## Decision ID: ODD-20
**Topic**: Extension of thirdPartyVerifier with Verification metadata
**Status**: OPEN / PROPOSITION

### Problem statement

The `thirdPartyVerifier` element requires properties like `verifierAccreditationId` and `verificationStatementUrl` (previously flat `thirdPartyVerifier.url`), which are not part of the standard IDTA `ContactInformation` submodel.

### Proposition

Extend the `thirdPartyVerifier` SMC (which uses the `ContactInformation` semantic ID) with these two specific EPD properties. Alternatively, a custom EPD SMC could wrap the `ContactInformation` element. The current implementation directly extends the `ContactInformation` SMC for simplicity.

**Compatibility impact**: Low
**Required reviewers**: IDTA working group, LCA experts

## Decision ID: ODD-21
**Topic**: Removal of orphaned `epdDeveloper.email` ConceptDescription
**Status**: OPEN / PROPOSITION

### Problem statement

A custom ConceptDescription `http://eclass.example.com/epdDeveloper.email` remains in the model after the `epdDeveloper` refactoring. It is not referenced by any SubmodelElement (the `epdDeveloper` SMC uses the standard IDTA `EmailAddress` SMC pattern, not this custom CD). It is an orphaned artifact with a placeholder semantic ID.

### Proposition

Remove the `epdDeveloper.email` ConceptDescription in the next cleanup pass. Email for `epdDeveloper` should be represented via the standard IDTA `ContactInformation/EmailAddress` SMC (consistent with `programOperator` and `thirdPartyVerifier`), not via a custom flat property.

**Compatibility impact**: Low (CD is not referenced by any SME)
**Required reviewers**: IDTA working group

## Decision ID: ODD-22
**Topic**: EPD instance granularity for homogeneous product families
**Status**: OPEN / PROPOSITION

### Problem statement
A published EPD may cover a homogeneous product family and provide multiplication/scaling factors for individual variants. A consuming system should ideally not need to interpret a multiplication-factor table before using environmental results.

### Proposition
Proposed long-term approach: one product AAS/SKU → one EPD Type III submodel instance → one complete, directly usable result set. A source EPD covering several variants may therefore result in several AAS EPD instances. Each instance may reference the same original Program Operator EPD document identifier while containing results already scaled to the relevant product variant.

**Questions**:
- Should multiplication-factor tables remain available as provenance/authoring information?
- Should receiving systems ever perform the multiplication?
- How should multiple AAS EPD instances reference one source EPD?
- How should the reference variant be retained?
- How should Type Assets vs Instance Assets be treated?

**Compatibility impact**: High
**Required reviewers**: IDTA working group, LCA experts

## Decision ID: ODD-23
**Topic**: Manufacturing-site modelling
**Status**: OPEN / PROPOSITION

### Problem statement
The `manufacturingSites` property represents the sites to which the EPD declaration/result set applies.

### Proposition
This property should not represent the complete upstream supply network, but only the final production sites or locations to which the EPD declaration directly applies.

**Questions**:
- What qualifies as a manufacturing site in the EPD context?
- Are allocation shares required?
- How should site-specific versus averaged EPD results be distinguished?

**Compatibility impact**: Medium
**Required reviewers**: IDTA working group, LCA experts

## Decision ID: ODD-24
**Topic**: Jurisdiction coding
**Status**: OPEN / PROPOSITION

### Problem statement
The model includes `applicableJurisdictions` but currently lacks a canonical geography coding system.

### Proposition
A canonical coding model must be selected. Consideration should include:
- ISO 3166-1 / ISO 3166-2
- UN M49
- Supranational regions (e.g. EU)
- Global applicability representation
- Mapping to openEPD Geography

Until agreed, jurisdiction is represented as a string property without enforcing a specific coding scheme.

**Compatibility impact**: Medium
**Required reviewers**: IDTA working group

## Decision ID: ODD-25
**Topic**: Biogenic carbon placement and interoperability
**Status**: OPEN / PROPOSITION

### Problem statement
Biogenic carbon content for both product and packaging needs to be modeled separately from generic total elemental carbon and separate from LCIA impact indicators.

### Proposition
- **Scope**: Represent `Biogenic carbon content in product` and `Biogenic carbon content in packaging` as separate additional/inventory indicators.
- **Semantic classification**: They are quantitative additional environmental/inventory information, not LCIA impact indicators or generic total carbon content.
- **Structural location**: Interim placement is a grouped structure within `manufacturerProduct`. The long-term standardized structure should place them under `additionalEnvironmentalInformation` or another dedicated non-LCIA EPD information section.
- **openEPD mapping**: `kg_C_biogenic_per_declared_unit` maps to product biogenic carbon. There is no direct openEPD core mapping currently available for packaging carbon.
- **Total elemental carbon**: openEPD's `kg_C_per_declared_unit` is intentionally **not part of the standardized EPD Type III core**.

**Compatibility impact**: Medium
**Required reviewers**: IDTA working group, LCA experts

## Decision ID: ODD-26
**Topic**: Representation of hierarchical PCR / PSR / c-PCR rule sets
**Status**: OPEN / PROPOSITION

### Problem statement
Different EPD programmes express applicable category rules differently:
- PCR + PSR
- PCR + c-PCR
- core PCR + programme PCR + c-PCR

Some external formats also express parent-child relationships between PCR documents.

### Current proposition
Represent all applicable rules as `productCategoryRules [SML]` with an explicit `ruleType` for each rule.

### Open question
Should future versions additionally model an explicit parent relationship between rules?
Possible approaches include:
- parent rule identifier
- AAS ReferenceElement
- generic relationship element
- external semantic reference

Do not implement a parent relationship yet unless an established repository pattern already solves this cleanly.

**Compatibility impact**: Medium
**Required reviewers**: IDTA working group

## Decision ID: ODD-27
**Topic**: Semantic roles for standards compliance
**Status**: OPEN / PROPOSITION

### Problem statement
The `standardsCompliance` list currently represents all normative standards with which the declaration or LCA explicitly claims conformity.

### Proposition
Keep the standards list simple and only include standards to which the source EPD explicitly claims relevant conformity. Do not implement a role taxonomy yet.

### Open question
Do entries in `standardsCompliance` need an explicit semantic role in the future?
Possible future roles might include:
- declaration standard
- LCA methodology standard
- core PCR standard
- product standard

**Compatibility impact**: Low
**Required reviewers**: IDTA working group
