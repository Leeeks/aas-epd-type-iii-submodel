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
