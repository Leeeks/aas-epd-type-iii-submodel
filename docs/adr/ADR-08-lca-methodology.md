# ADR-08: LCA Methodology and Provenance Boundary

## Context

An EPD Submodel contains data derived from a Life Cycle Assessment (LCA). To correctly interpret the environmental results, downstream consumers need the metadata describing how that LCA was conducted—the `LCAMethodology`. Concurrently, there is a need to understand the provenance of the AAS instance itself (e.g., how the EPD was converted into an AAS). The current model mixes these concepts and occasionally includes highly specific implementation artefacts (like ILCD or openLCA dataset IDs) that hold no independent exchange value outside of those specific software tools.

## Source constraints

* EN 15804 and PCRs require declaration of representativeness (time, geography, technology), allocation rules, cut-off criteria, and the LCIA method used.
* The AAS must serve as an interoperable exchange format, independent of the specific LCA software (e.g., SimaPro, openLCA, Sphera) used to calculate the results.

## Requirements

The chosen architecture must:
* Group downstream interpretation concepts under a generic `LCAMethodology` structure.
* Separately identify provenance information about how the AAS instance was generated.
* Remove implementation-specific software artefacts unless they serve a universal EPD exchange purpose.

## Option A

**Mixed Metadata Structure**

Structure: A flat list of metadata properties at the root of the EPD Submodel, mixing LCA methodology (like reference year) with AAS generation provenance (like conversion script version) and internal software UUIDs.

**Advantages:**
* Simple flat structure.

**Disadvantages:**
* Confuses the end-user about what metadata applies to the physical product's LCA vs the digital file's creation.
* Leaks proprietary or irrelevant software IDs into an open standard, causing confusion.

## Option B

**Strict Separation: LCAMethodology vs Provenance**

Structure: 
1. Create a dedicated `LCAMethodology` SML containing properties essential for LCA interpretation: Reference Year, Time Representativeness, Geographical Representativeness, Technology Description, LCIA Method, Allocation Rules, Cut-off Rules, Primary Data Share, and generic names for the LCA Software and Database used.
2. Create a separate `AasProvenance` (or similar) section to track how the digital shell was generated from the source EPD.
3. Explicitly purge internal ILCD/openLCA UUIDs from the main schema, as they are not standard EPD exchange parameters. (If a user needs them, they can add them via custom properties, but they do not belong in the standardized submodel).

Example AAS hierarchy:
```
EPD Submodel
├── LCAMethodology [SML]
│   ├── ReferenceYear: 2023
│   ├── GeographicalRepresentativeness: "EU"
│   ├── LciaMethod: "EN 15804+A2 Method"
│   └── LcaDatabase: "Ecoinvent 3.9"
└── AasProvenance [SML]
    └── GenerationTool: "WAGO AAS Converter v1.2"
```

**Advantages:**
* Clean separation of concerns. LCA practitioners get exactly the methodology data they need without sorting through IT metadata.
* Removes tool bias (ILCD/openLCA) from the standardized interoperability model.

**Disadvantages:**
* None significant.

## Recommendation

**Option B** is recommended. The EPD Submodel must clearly separate the scientific methodology of the LCA from the digital provenance of the AAS instance. By grouping LCA parameters under `LCAMethodology` and purging tool-specific internal IDs (like ILCD UUIDs) from the standard schema, we create a clean, tool-agnostic interoperability format.

## Consequences

* **What becomes easier:** LCA practitioners can instantly find the quality and representativeness metrics they need to decide if an EPD is suitable for their building or product assessment.
* **What becomes harder:** Nothing, it merely organizes existing data more logically.

## Programme compatibility

* **PEP ecopassport:** Compatible.
* **EPD International non-construction:** Compatible.
* **EPD International construction / EN 15804:** Compatible.

## Downstream consumer perspective

A consumer will read the `LCAMethodology` to check if the EPD's geographical scope and reference year match their requirements (e.g., ensuring they aren't using 10-year-old data for a modern assessment). They can safely ignore `AasProvenance` unless they are debugging a data conversion error.

## Breaking change impact

* **Medium**. Reorganizes existing metadata properties (like `representativenessReference`) into a cohesive `LCAMethodology` SML and removes irrelevant software-specific fields.

## Open questions

* None.
