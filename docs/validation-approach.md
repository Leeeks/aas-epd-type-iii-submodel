# Validation Approach

## Purpose
This approach describes the method for validating the EPD Type III Submodel Template using real EPD data, specifically the WAGO PEP Ecopassport publication WAGO-00001-V01.01-EN.

## Test criteria
1. **Structural integrity**: Conformity of the AASX archives (ZIP) and the included XML/JSON data to the AAS metamodel V3.0.
2. **Technical completeness**: All core information contained in the reference PDF must be mappable in the AAS Submodel without technical loss.
3. **Extensibility**: Dynamic indicator and life cycle lists must be easily poputable upon instantiation, maintaining unique `idShort`s within the respective lists.
4. **Referencing**: Existing standards (ISO 14025, EN 15804) and program operator specifications must be correctly referenced.
