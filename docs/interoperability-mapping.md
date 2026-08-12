# Interoperability Mapping

This document describes the planned or existing compatibility with EPD-specific standards and formats.

## openEPD JSON Interoperability Mapping Matrix

The IDTA EPD Type III Submodel preserves full bidirectional mapping capability with openEPD JSON schema (v0.1 / v1.0). Transport-specific or schema-wrapper fields in openEPD are mapped to/from domain data properties as follows:

| openEPD JSON Field | AAS EPD Type III Submodel Element | Mapping Direction & Notes |
|---|---|---|
| `id` (openEPD UUID) | `documentIds` `[documentDomainId="openEPD"].documentIdentifier` | ↔ Bidirectional. Represented as a non-primary document identifier in `documentIds` SML. |
| `program_operator_doc_id` | `documentIds` `[documentIsPrimary=true].documentIdentifier` | ↔ Bidirectional. Primary document identifier assigned by the Program Operator. |
| `alt_ids` | `documentIds` `[documentDomainId=...].documentIdentifier` | ↔ Bidirectional. Additional external document identifiers (e.g. ILCD UUID). |
| `program_operator_version` | `programOperatorVersion` | ↔ Bidirectional. EPD document version issued by the Program Operator (e.g. `V01.01-EN`). |
| `date_of_issue` | `dateOfIssue` | ↔ Bidirectional. ISO date format (`YYYY-MM-DD`). |
| `valid_until` | `validUntil` | ↔ Bidirectional. ISO date format (`YYYY-MM-DD`). |
| `language` | `languages` `[Property]` | ↔ Bidirectional. Represented as ISO 639-1 two-letter language code string in `languages` SML. |
| `declaration_url` | `declarationUrl` | ↔ Bidirectional. Direct URL link to official publication record. |
| `original_data_format` | `sourceDataFormat` | ↔ Bidirectional. Source format provenance string (e.g. `openEPD`, `PEP Ecopassport PDF`). |
| `program_operator` (Org Object) | `programOperatorVerification/programOperator` | ↔ Bidirectional. Mapped to IDTA ContactInformation (e.g., openEPD name to `Company`). |
| `third_party_verifier` (Org Object) | `programOperatorVerification/thirdPartyVerifier` | ↔ Bidirectional. Mapped to IDTA ContactInformation (e.g., openEPD name to `Company`). |
| `third_party_verifier_email` | `.../thirdPartyVerifier/EmailAddress/EmailAddress` | ↔ Bidirectional. Mapped to IDTA ContactInformation nested EmailAddress property. |
| `epd_developer` (Org Object) | `programOperatorVerification/epdDeveloper` | ↔ Bidirectional. Mapped to IDTA ContactInformation (e.g., openEPD name to `Company`). |
| `epd_developer_email` | `.../epdDeveloper/EmailAddress/EmailAddress` | ↔ Bidirectional. Mapped to IDTA ContactInformation nested EmailAddress property. |
| `doctype` | *(Excluded from Submodel)* | ➔ openEPD serialization layer. Hardcoded transport type (e.g., `"openEPD"`), handled by openEPD converter. |
| `openepd_version` | *(Excluded from Submodel)* | ➔ openEPD serialization layer. Transport schema version, handled by openEPD converter. |
| `private` | *(Excluded from Submodel)* | ➔ Transport / Access control layer. Handled by AAS Access Control / API authorization policies. |
| `version` (record version) | *(Excluded from Submodel)* | ➔ AAS Administrative Information (`submodel.administration.revision`). |

## Implementation status
- **PEP Ecopassport**: Partially mapped, validated by WAGO-00001-V01.01-EN.
- **EN 15804**: Partially mapped, basis for LCIA indicators.
- **ISO 14025**: Basic structure mapped.
- **openEPD JSON**: Interoperability mapping matrix defined above.

## Planned integrations
- **ILCD+EPD XML**: Planned.
- **ECO Platform**: Planned, validation pending.
- **EN 50693**: Planned.
- **Digital Product Passport (DPP)**: Planned.
- **International EPD System**: Not yet validated.
- **AAS-based data provision**: Fully implemented (Goal of this submodel).
