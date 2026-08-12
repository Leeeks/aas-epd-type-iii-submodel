# Changelog

## Unreleased – Working Draft

- Implemented dynamic idShort values for `lciaResults`.
- Implemented dynamic idShort values for `lifeCyclePhaseValues`.
- Compact modeling of `characterizationUnit`.
- Introduced optional `baseUnit`.
- Validation with WAGO-00001-V01.01-EN successfully performed.
- Documented identified redundancies.
- Documented identified model gaps.
- Documented known AAS version topics.
- **IEC 61360 correction**: Removed `dataType = REAL_MEASURE` from the generic
  `LifeCyclePhaseValue` ConceptDescription. The concept covers values with different
  characterization units depending on the LCIA indicator; a fixed unit cannot be
  assigned at this abstraction level. The `dataType` field is now left unspecified.
  The `valueType = xs:decimal` on the actual AAS Property is unchanged.
- **IEC 61360 correction**: Added the required `<value>` literal to all 37 indicator
  enumeration ConceptDescriptions referenced via `ValueReferencePair.valueId` from the
  `indicatorCode` ValueList (GWP-total, GWP-fossil, GWP-biogenic, GWP-luluc, ODP, AP,
  EP-freshwater, EP-marine, EP-terrestrial, POCP, ADPE, ADPF, WDP, PM, IRP, ETP-fw,
  HTP-c, HTP-nc, SQP, PERT, PENRT, PERM, PENRM, SM, RSF, NRSF, FW, PERE, PENRE, HWD,
  NHWD, RWD, CRU, MFR, MER, EEE, EET). The `dataType` remains `STRING` as these CDs
  represent enumeration values, not quantitative properties.
- Added ODD-15: Proposition for indicator-specific quantitative ConceptDescriptions
  (`REAL_MEASURE` + `unit` + `isCaseOf → LifeCyclePhaseValue`). Marked as open for
  working-group discussion. **Not implemented.**
- **Refactored `identificationPublication` semantics**:
  - Replaced single `epdId` and `registrationId` properties with `documentIds`
    `SubmodelElementList` containing `documentId` `SubmodelElementCollection` elements
    (pattern based on IDTA Handover Documentation / VDI 2770). Supports multiple document
    identifiers for the same EPD (e.g. primary Program Operator ID and openEPD UUID).
  - Renamed `version` to `programOperatorVersion` to explicitly represent the EPD document
    version issued by the Program Operator.
  - Replaced single `language` property with `languages` `SubmodelElementList` containing ISO 639-1
    two-letter language code properties.
  - Renamed `originalDataFormat` to `sourceDataFormat`.
  - Added optional `declarationUrl` property (0..1) linking to official online publication.
  - Removed openEPD transport and application database fields from core domain model:
    `doctype`, `private`, `epdType`, `lastChange`, and `tags`.
  - Replaced all placeholder `http://example.com/` and `http://eclass.example.com/` semantic IDs
    in `identificationPublication` with authoritative IDTA, VDI 2770, and ECLASS semantic IDs.
- Added **ODD-16** (EPD Publication/Lifecycle Status vs. Access Control), **ODD-17** (Incomplete
  Date Precision), and **ODD-18** (Provenance Metadata Placement).
- Updated openEPD JSON interoperability mapping matrix in `docs/interoperability-mapping.md`.
