# Project status
> **Working Draft** – For working-group review
> Not an official IDTA release

## Purpose
Development of an interoperable AAS Submodel Template for EPD Type III, mapping of environmental information according to ISO 14025, consideration of typical EPD programs and exchange formats, validation using a real PEP Ecopassport publication.

## Scope
- EPD identification
- Product and manufacturer information
- PCR and PSR references
- Declared or functional unit
- System boundaries
- LCIA results
- Life cycle phases
- Characterization units
- Verification
- Document references

## Non-scope
- Complete LCA modeling
- Calculation of environmental impacts
- Program operator-specific publication processes
- Legally binding verification
- Replacement of the original EPD PDF

## Data model
A complete UML representation of the EPD Type III submodel is available here:

[View complete UML model](docs/model/epd-type-iii-model.svg)

## Repository structure
- `model/template`: The generic EPD Type III AAS Submodel Template
- `examples/wago-00001`: WAGO example instance, mapping, and source PDF
- `docs`: Architecture, interoperability mapping, and ADRs
- `docs/review`: Review comments and history
- `validation`: Validation reports and checksums

## Main artifacts
- [Template](model/template/epd-type-iii-submodel-template.aasx)
- [WAGO Example Instance](examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx)
- [PEP Mapping](examples/wago-00001/mapping/wago-00001-to-epd-submodel-mapping.json)
- [Review Document](docs/review/epd-type-iii-submodel-change-review.md)
- [Open Design Decisions](docs/open-design-decisions.md)
- [ADRs](docs/adr/0001-dynamic-idshort-for-lcia-results.md)
- [Validation Report](validation/epd-type-iii-submodel-validation-report.md)

## Quick start
1. Open AASX Package Explorer.
2. Load template or example instance.
3. Check `lciaResults`.
4. Check `lifeCyclePhaseValues`.
5. Submit review comments via GitHub Issues.

## Current model features
- Dynamic LCIA indicator list
- Dynamic life cycle phase list
- Instance-specific idShort
- Complete LCIA characterization unit
- Optional ECLASS base unit
- Mapping of mandatory and optional environmental indicators

## Known limitations
See [Open Design Decisions](docs/open-design-decisions.md).

## Contribution and review
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [Reviewer Guide](docs/reviewer-guide.md)

## License
See [LICENSE_DECISION_REQUIRED.md](LICENSE_DECISION_REQUIRED.md).
