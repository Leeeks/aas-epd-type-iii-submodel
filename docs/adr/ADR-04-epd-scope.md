# ADR-04: EPD Scope / Multi-Product EPDs

## Context

EPDs are frequently published as "family", "average", "representative", or "worst-case" declarations that cover a wide range of physical product variants. However, an Asset Administration Shell (AAS) is fundamentally designed to represent a specific Asset—either an *Asset Type* (a catalog product) or an *Asset Instance* (a physical manufactured serial number). We must decide how to model the relationship between the scope of an EPD and the scope of the AAS it is attached to, without forcing the AAS to violate its core principles by embedding massive product-family extrapolation matrices.

## Source constraints

* Programs explicitly support single-product, multi-product, family, representative, average, and worst-case EPDs.
* Multi-product EPDs often require applying scaling factors or variant-specific calculations to derive the exact results for a specific item.
* The AAS metamodel distinguishes explicitly between Asset Type and Asset Instance.

## Requirements

The chosen architecture must:
* Explicitly distinguish between Asset Instance, Asset Type, and the EPD declaration scope.
* Identify whether the EPD is single-product, multi-product, family, representative, average, or worst-case.
* Avoid turning the EPD Submodel into a complex product-family calculation engine unless justified.
* Ensure the EPD Submodel accurately states exactly what its environmental results represent in the context of its parent AAS.

## Option A

**Family EPDs Fully Encoded Inside the AAS Submodel**

Structure: The EPD Submodel includes a massive matrix containing the extrapolation rules, scaling factors, and variant parameters for the entire product family.
Example AAS hierarchy:
```
EPD Submodel
├── Scope: "Family EPD"
├── Variants [SML] (Lists every possible configuration)
└── ResultsMatrix (Complex multi-dimensional array)
```

**Advantages:**
* Delivers the entire EPD document context in one shell.

**Disadvantages:**
* Grossly violates the AAS paradigm: a shell describes *its* asset, not the entire family of theoretical assets.
* Unmanageable implementation complexity for consumers who just want the footprint of the item in front of them.

## Option B

**EPD Submodel Restricted Only to Fully Resolved Values**

Structure: The EPD Submodel only ever contains the exact, resolved values for the specific Asset Type or Instance it is attached to. It makes no mention of the wider family.

**Advantages:**
* Highly aligned with the AAS philosophy.
* Extremely simple for downstream consumers to read.

**Disadvantages:**
* Loses critical provenance data. A consumer cannot tell if the data is a highly accurate single-product LCA or a heavily extrapolated worst-case estimate.

## Option C

**EPD Declaration Scope Referencing Multiple Products**

Structure: The Submodel lists all product identifiers covered by the EPD.

**Advantages:**
* Mimics the "Products covered" table of an EPD.

**Disadvantages:**
* Bloats the shell with irrelevant identifiers that do not belong to the specific Asset the shell represents.

## Option D

**Hybrid: Resolved Payload with Explicit Scope Meta-Data**

Structure: The EPD Submodel provides the specific, calculated environmental results for the Asset (Type or Instance) it is attached to. It includes an `EpdScope` metadata SML that describes the *origin* of this data: whether it came from a single-product EPD, a family EPD, or an average. If it came from a family EPD, it links to the original EPD identifier, but does *not* include the extrapolation math or lists of other product variants.

Example AAS hierarchy:
```
EPD Submodel
├── EpdScope [SMC]
│   ├── DeclarationScope: "Family Average"
│   └── SourceEpdReference: "EPD-12345"
└── EnvironmentalResults (Resolved values for THIS asset)
```

**Advantages:**
* Honors the AAS paradigm: the submodel represents the Asset.
* Retains critical provenance data regarding the *quality* and *scope* of the LCA data.
* Consumers get simple, direct values without needing to execute complex scaling math.

**Disadvantages:**
* Requires publishers to pre-calculate or resolve the family EPD into specific values before generating the AAS.

## Recommendation

**Option D** is recommended. The EPD Submodel must accurately state what the EPD results represent regarding the attached Asset. We must not force family EPD extrapolation logic into the Submodel. The publisher (or an explicit transformation process) should resolve the values for the specific Asset (Type or Instance) and populate the AAS with those explicit results, while using `EpdScope` to transparently declare that these values were derived from a multi-product or representative EPD.

## Consequences

* **What becomes easier:** Downstream consumers (e.g., carbon accounting tools) can read explicit values directly without needing to interpret complex product-family formulas.
* **What becomes harder:** Publishers of complex multi-product EPDs must generate individual resolved Submodels for their Asset Types, rather than dumping one massive generic formula into a single Submodel.

## Programme compatibility

* **PEP ecopassport:** Compatible. Supports their extrapolation rules by assuming the results provided in the AAS are the *post-extrapolation* results for that specific Asset Type.
* **EPD International non-construction:** Compatible.
* **EPD International construction / EN 15804:** Compatible.

## Downstream consumer perspective

Consumers will check the `EpdScope`. If it says "Representative EPD", they understand the data is a generalization. They can then read the `EnvironmentalResults` and directly apply them to the asset, trusting that the values provided apply precisely to the AAS they are querying.

## Breaking change impact

* **Low**. This primarily involves adding structural metadata (`EpdScope`) to classify the origin of the data.

## Open questions

* None.
