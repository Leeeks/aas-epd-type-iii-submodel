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
