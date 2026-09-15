# LCAMethodology Semantic Review

This document contains the final focused semantic review of the `LCAMethodology` section of the AAS EPD Type III Submodel. The review was conducted against the PEP ecopassport PCR Edition 4, EPD International GPI 5.0.1, and corresponding templates to ensure all properties have a justified programmatic Type III EPD data exchange use case.

## Final LCAMethodology hierarchy

The following hierarchy represents the cleaned, canonical `LCAMethodology` structure implemented in the submodel (with cardinalities):

```text
LCAMethodology [SMC, mandatory]
├── lcaReferenceYear [Property, xs:string, 1]
├── timeRepresentativenessDescription [Property, xs:string, 0..1]
├── geographicalScope [Property, xs:string, 1]
├── geographicalDescription [Property, xs:string, 0..1]
├── technologyDescription [Property, xs:string, 0..1]
├── lcaEnergyModel [Property, xs:string, 1]
└── DeclaredStages [SML, 1]
```

## Removed properties

The following properties were entirely removed from the standard because they lack an independent Type III EPD use case:

* **`dataSetValidUntil`**: This is a pure ILCD / openLCA software artefact used to declare the validity of an underlying life cycle dataset. It has no bearing on the published EPD document itself, whose validity is already securely and correctly declared in `identificationPublication/validUntil`. Retaining it created semantic redundancy and confusion.
* **`technicalPurpose`**: Another legacy ILCD artefact. The technical function and purpose of the product in an EPD is properly described by the `FunctionalUnit` definition (or `productDescription` in `manufacturerProduct`). A generic methodology field for it was redundant.

## Renamed / merged properties

Properties that were semantically valid but ambiguously named were renamed to explicitly state their EPD meaning:

* **`referenceYear` → `lcaReferenceYear`**: The generic term "reference year" is highly ambiguous—it could refer to publication year, product launch, etc. EPD Int'l GPI §6 explicitly requires the "Reference year for background data" and PEP requires it for primary data. The prefix clarifies that this is the reference year of the LCA study.
* **`location` → `geographicalScope`**: "Location" is vague and can be confused with manufacturing site addresses. "Geographical scope" directly matches EPD International's and PEP's requirement to explicitly define the geographical boundary for the EPD's validity (e.g., "GLO", "EU-27").
* **`energyModel` → `lcaEnergyModel`**: Clarifies that this string refers to the specific background energy scenario or electricity mix used in the LCA (e.g., the manufacturing phase electricity mix, as required by PEP and EN 15804).

## Retained properties

* **`timeRepresentativenessDescription`**: A narrative text describing the temporal representativeness of the data (e.g., how well the primary data matches the reference year). Useful for downstream LCA practitioners verifying data quality against EN 15804 requirements.
* **`geographicalDescription`**: A narrative text expanding on `geographicalScope`. While the scope might be "DE", the description can explain specific geographical constraints of the supply chain.
* **`technologyDescription`**: A narrative describing the specific technology (e.g., manufacturing processes) represented by the LCA. Required for data quality assessment under EN 15804 and EPD Int'l.
* **`DeclaredStages`**: Retained as the canonical representation of which life cycle stages (A1-D) have been assessed or omitted in the methodology boundary. 

## Mandatory vs optional

The cardinalities were strictly audited to separate *template requirements* from *example completeness*:

* **Mandatory `[1]` fields**: 
  * `lcaReferenceYear`, `geographicalScope`, `lcaEnergyModel`: These three fields describe the absolute core methodological constraints of the LCA (When? Where? With what power?). Omitting them makes the environmental results virtually uninterpretable for a downstream consumer integrating the EPD into a building-level or system-level LCA. They are mandatory in both PEP and EPD Int'l.
  * `DeclaredStages`: The system boundary must be defined to interpret the results.
* **Optional `[0..1]` fields**: 
  * `timeRepresentativenessDescription`, `geographicalDescription`, `technologyDescription`: While EN 15804 requires data quality descriptions in the background report, these lengthy narratives are often summarized or omitted in the machine-readable summary. Making them mandatory would break interoperability for EPDs that do not provide exhaustive text narratives. They are therefore appropriately optional.

## Source traceability

| Property | Source Justification |
| :--- | :--- |
| `lcaReferenceYear` | EPD Int'l GPI 5.0.1 (§6) / PEP PCR |
| `timeRepresentativenessDescription` | EN 15804 (Data quality) / EPD Int'l |
| `geographicalScope` | EPD Int'l GPI 5.0.1 (§6) / PEP PCR |
| `geographicalDescription` | EN 15804 (Data quality) / EPD Int'l |
| `technologyDescription` | EN 15804 (Data quality) / EPD Int'l |
| `lcaEnergyModel` | PEP PCR ("Energy model used") / EPD Int'l ("Electricity used in manufacturing") |
| `DeclaredStages` | EN 15804 / EPD Int'l / PEP PCR |
