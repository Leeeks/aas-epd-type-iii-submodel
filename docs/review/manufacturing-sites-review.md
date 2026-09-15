# ManufacturingSites Architectural Review

This document contains the final architectural review and refactoring of the `ManufacturingSites` area of the AAS EPD Type III Submodel. The objective was to create a robust, programme-independent representation that correctly captures complex scenarios (contract manufacturing, mobile plants, location precision) without over-engineering the submodel into a generic facility management tool.

## Source Findings

1. **PEP ecopassport & EPD International**: Manufacturing-site or geographical production information is relevant in the tested EPD programme requirements. It supports the interpretation of geographical representativeness, transportation logistics, and electricity modeling assumptions for the life cycle assessment.
2. **Contract Manufacturing**: The product manufacturer (brand owner) and the physical site operator may differ. The model must accommodate this distinction without introducing confusing heuristics.
3. **Location Precision**: Some sites are mobile (e.g., mobile asphalt plants) where exact point coordinates are meaningless, but regional operating areas remain relevant.

## openEPD Interoperability Comparison

The **openEPD format** models a manufacturing facility as a `plant`, which is uniquely identified by combining the manufacturer and an Open Location Code (OLC / Plus Code). This provides a stable, "natural ID".
While openEPD heavily uses the Open Location Code to solve fuzzy geospatial matching, the AAS EPD Type III Submodel must integrate natively with standard AAS paradigms. Thus, a stable `siteIdentifier` combined with explicit hierarchical `Location` components provides the best balance of robust AAS architecture and openEPD semantic compatibility.

## Final ManufacturingSites hierarchy

The following canonical hierarchy was implemented. The old `siteName`, `siteCountry`, and `siteCity` flat properties were superseded by this structured approach.

```text
ManufacturingSites [SML, 0..*]
└── ManufacturingSite [SMC]
    ├── SiteIdentifiers [SML, 0..1]
    │   └── SiteIdentifier [SMC, 0..*]
    │       ├── identifierScheme [Property, xs:string, 1]
    │       └── identifierValue [Property, xs:string, 1]
    ├── siteName [Property, xs:string, 0..1]
    ├── siteType [Property, xs:string, 0..1]
    ├── siteOperator [Property, xs:string, 0..1]
    └── Location [SMC, 0..1]
        ├── countryCode [Property, xs:string, 0..1]
        ├── region [Property, xs:string, 0..1]
        ├── locality [Property, xs:string, 0..1]
        ├── latitude [Property, xs:decimal, 0..1]
        ├── longitude [Property, xs:decimal, 0..1]
        └── LocationCodes [SML, 0..1]
            └── LocationCode [SMC, 0..*]
                ├── codingSystem [Property, xs:string, 1]
                └── code [Property, xs:string, 1]
```

## Existing structure migration

The legacy root-level properties were migrated as follows:
* `manufacturerProduct/manufacturingSites/siteName` ➔ **Retained** as `ManufacturingSite/siteName`.
* `manufacturerProduct/manufacturingSites/siteCountry` ➔ **Moved** to `ManufacturingSite/Location/countryCode`.
* `manufacturerProduct/manufacturingSites/siteCity` ➔ **Moved** to `ManufacturingSite/Location/locality`.

## Removed / rejected concepts

* **`siteOwner`**: **Rejected**. The legal owner of the physical real estate does not affect the LCA processes. The `siteOperator` concept successfully resolves contract manufacturing ambiguity without requiring real estate ownership data.
* **`locationPrecision` / `locationTolerance` (e.g., `200m`)**: **Rejected**. A fuzzy geographical tolerance distance is a downstream application matching problem, not a semantic property of the data exchange model. Precision is better handled by grid-based location codes (like OLC/Plus Codes) via `LocationCode`, which inherently specify a bounding box instead of an arbitrary radius.
* **`primaryDataShare`**: **Rejected**. Supply-chain specificity scores belong in LCA Methodology or Data Quality objects, not the physical site object.
* **`locationCode` (flat string)**: **Superseded** by the `LocationCodes` [SML] and `LocationCode` [SMC] structure to explicitly capture the coding system used (e.g., "Open Location Code") and allow multiple codes.
* **`siteIdentifier` (flat string)**: **Superseded** by the `SiteIdentifiers` [SML] and `SiteIdentifier` [SMC] structure to allow multiple explicit identifier schemes (e.g., openEPDPlantID, DUNS) without assuming a default generic identity mechanism. Note: if DUNS is used, it identifies the legal organization at the location, not necessarily the physical facility boundary.

## Site identity strategy

Downstream consumers should rely on explicit `SiteIdentifier` structures (e.g., an openEPD plant ID or internal code) to establish absolute semantic equivalence. Geographical location (`latitude`, `longitude`, `LocationCode`) provides strong matching evidence, but shouldn't be used as the sole determinant of identity, since coordinates may refer to a front gate vs. the center of a plant.

## Contract manufacturing

Contract manufacturing is natively supported. The top-level `manufacturerProduct/manufacturerName` correctly holds the name of the manufacturer associated with the product declared in the EPD, according to the source declaration (this entity may differ from the physical site operator). The specific `ManufacturingSite/siteOperator` holds the legal entity actually operating the manufacturing activities at the physical site (e.g., "Contract Manufacturer XYZ"). These properties do not semantically conflict.

## Mobile plants

Mobile manufacturing plants are fully supported by defining the controlled vocabulary `siteType="Mobile"`. In this case, `latitude` and `longitude` are omitted, and only `Location/countryCode` and `Location/region` are populated, representing the plant's operational theater.

## Example data provenance

The generated WAGO example (`wago-00001-v01-01-en-epd-submodel-instance.aasx`) now contains two example sites with properly classified data provenance:
1. **Normal fixed manufacturing site**: Uses the real-world Minden Plant. Note that while the plant is **SOURCE-DERIVED** from the EPD, the exact precise decimal coordinates and Open Location Code are marked as **EXTERNALLY ENRICHED EXAMPLE DATA**, as such highly precise values are typically absent from standard PEP PDFs.
2. **Contract manufacturing / mobile site**: A synthetic example demonstrating a mobile plant in France operated by "Contract Manufacturer XYZ". This entry is purely **ILLUSTRATIVE** to prove the structure handles abstract regional bounds without hard coordinates.

## Files changed

* `docs/model/epd-type-iii-model.puml` (PUML architecture)
* `scripts/patch_template_aasx.py` (Template patch logic)
* `scripts/generate_wago_instance.py` (Population of WAGO example)
* `validation/SHA256SUMS` (Hashes updated)

## Validation results

1. The `ManufacturingSites` property is a repeatable list.
2. The example correctly demonstrates both fixed and mobile site representations.
3. Country/region is structurally independent from latitude/longitude.
4. `siteOperator` correctly accommodates contract manufacturing.
5. Legacy properties (`siteCountry`, `siteCity`) were fully removed.
6. Only one canonical location structure exists.
