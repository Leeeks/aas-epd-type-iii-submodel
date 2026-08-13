# Validation Report

**Test object**: EPD Type III Submodel Template and WAGO example instance
**Method used**: Automated conversion and manual check against source PDF
**Tool used**: Python-based conversion scripts (AAS Excel Conversion Tool)
**Tool version**: N/A (Script-based)

## Results

| Test point | Result | Cause / Measure | Release relevance |
| :--- | :--- | :--- | :--- |
| ZIP integrity of AASX files | **passed** | | No |
| Correct AASX package structure | **passed** | | No |
| XML/JSON readability | **passed** | | No |
| Used AAS metamodel version | **passed** | V3.0 | No |
| `kind = Template` | **passed** | | No |
| `kind = Instance` | **passed** | | No |
| Unique `idShort` | **passed** | | No |
| Preservation of LCIA `idShort` | **passed** | Dynamic naming | No |
| Preservation of phase `idShort` | **passed** | Dynamic naming | No |
| Consistent `semanticIdListElement` | **passed** | | No |
| Consistent `typeValueListElement` | **passed** | | No |
| Consistent `valueTypeListElement` | **passed** | | No |
| No broken references | **passed** | | No |
| `LifeCyclePhaseValue` has no `REAL_MEASURE` | **passed** | IEC 61360 correction applied | No |
| All `indicatorCode` ValueList CDs have matching `<value>` | **passed** | 37 CDs corrected | No |
| Numeric LCIA values unchanged | **passed** | Verified by re-extraction | No |
| `documentIds` multi-ID structure | **passed** | Handover Doc / VDI 2770 pattern | No |
| Refactored `identificationPublication` semantics | **passed** | Transport/app fields removed, version/languages clarified | No |
| Refactored `programOperatorVerification` semantics | **passed** | Flat fields removed in favor of IDTA ContactInformation SMCs | No |
| `epdDeveloper/Company` MLP structure | **passed** | `Company` [MLP, `0173-1#02-AAW001#001`] added; `RoleOfContactPerson` CD (wrong IRDI `0173-1#02-AAQ836#005`) removed; custom `epdDeveloper.name` CD removed | No |
| Authoritative Semantic IDs | **passed** | All placeholder `example.com` IDs in `identificationPublication` eliminated | No |
| Embedded PEP file accessible | **warning** | Legal clarification for PDF publication is missing. | **Release blocker** |
| Use of `idShort` in list elements | **warning** | AAS V3.0 conformity of `idShort` on direct list elements must be validated. | **Release blocker** |
| `issueDate` incomplete | **warning** | Documented in ODD-17. | Medium |
| Placeholder Semantic IDs | **warning** | Submodel-wide cleanup ongoing (identificationPublication complete). | **Release blocker** |
| `Total` as life cycle phase | **warning** | Not standard-compliant with specific phases. | Medium |
