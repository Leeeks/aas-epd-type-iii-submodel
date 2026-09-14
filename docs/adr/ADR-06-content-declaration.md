# ADR-06: Content Declaration Architecture

## Context

The Content Declaration is a fundamental component of a Type III EPD for physical products, detailing the composition of the product (materials, substances, mass, recycled content, biogenic carbon, etc.). However, EPDs can also be issued for intangible products (e.g., services) where a content declaration is completely irrelevant. Furthermore, the Asset Administration Shell (AAS) ecosystem may eventually have dedicated submodels for material composition (e.g., a Material Passport). We must decide how to model the Content Declaration within the EPD Submodel without turning it into a universal, overly complex material-compliance tracking system.

## Source constraints

* EPD International GPI explicitly states that content declaration may not be relevant for services.
* Construction EPDs (EN 15804) require reporting biogenic carbon content in the product and packaging.
* General EPDs require reporting material composition, mass percentages, and hazardous substances (if applicable).

## Requirements

The chosen architecture must:
* Support modeling `ContentDeclaration [0..1]` (optional at the schema level).
* Provide structures for product composition, packaging composition, materials, substances, mass, mass percentage, recycled content, and biogenic carbon.
* Determine which concepts belong natively in the EPD Submodel and which should reference other AAS submodels.
* Avoid turning the EPD Submodel into a full Material BOM.

## Option A

**Comprehensive Content Declaration Native to the EPD Submodel**

Structure: A deeply nested, highly detailed `ContentDeclaration` SML within the EPD Submodel, capable of modeling every chemical substance, material layer, and mass percentage for both the product and its packaging.

**Advantages:**
* Self-contained. Consumers only need the EPD Submodel to read the entire material composition.

**Disadvantages:**
* Massive scope creep. Duplicates the functionality of dedicated Material Passport or Digital Product Passport (DPP) submodels.
* Makes the EPD Submodel excessively complex.

## Option B

**High-Level Content Summary with External References**

Structure: An optional `ContentDeclaration [0..1]` SML in the EPD Submodel that captures *only* the specific material metrics required by EPD standards to contextualize the LCA results. This includes: Total Mass, Recycled Content (%), Biogenic Carbon Content (Product), and Biogenic Carbon Content (Packaging). For detailed material/substance breakdowns, the `ContentDeclaration` provides a reference (ReferenceElement) to a dedicated Material BOM or DPP Submodel if one exists.

Example AAS hierarchy:
```
EPD Submodel
└── ContentDeclaration [0..1]
    ├── ProductMass [SMC]
    ├── BiogenicCarbonContentProduct [SMC]
    ├── BiogenicCarbonContentPackaging [SMC]
    ├── RecycledContentPercentage [SMC]
    ├── HazardousSubstancesDeclared [Property/Boolean]
    └── MaterialBomReference [ReferenceElement] (Points to another Submodel)
```

**Advantages:**
* Keeps the EPD Submodel focused strictly on LCA-relevant parameters.
* Avoids reinventing a Material Passport inside an environmental standard.
* `0..1` cardinality cleanly supports service EPDs.

**Disadvantages:**
* Consumers needing the full chemical breakdown must resolve a reference to another submodel.

## Recommendation

**Option B** is recommended. The EPD Submodel should not become a universal material-compliance model. It should capture the high-level mass, biogenic carbon, and recycled content metrics that directly contextualize the LCA results (as required by EN 15804 and general PCRs), while leaving deep substance-level BOMs to specialized material submodels via a reference. The `ContentDeclaration` must be optional `[0..1]` to support EPDs for services.

## Consequences

* **What becomes easier:** Developing and maintaining the EPD Submodel, as we do not have to model complex chemical compliance hierarchies.
* **What becomes harder:** Consumers wanting both LCA data and a full chemical breakdown must parse two different AAS submodels.

## Programme compatibility

* **PEP ecopassport:** Compatible. Mass and high-level composition can be declared.
* **EPD International non-construction:** Compatible. Supports the requirement for service EPDs to omit this section.
* **EPD International construction / EN 15804:** Compatible. Explicitly supports the mandatory declaration of biogenic carbon in product and packaging.

## Downstream consumer perspective

A consumer evaluating carbon data will read the `ContentDeclaration` to find the biogenic carbon and total mass—critical parameters for scaling or interpreting the LCA results. If they need to perform REACH/RoHS compliance checks, they will follow the `MaterialBomReference` to the appropriate submodel.

## Breaking change impact

* **Medium**. Re-scopes the existing material properties to focus on LCA-relevant summary metrics rather than a full BOM.

## Open questions

* Which specific AAS submodel standard should be the recommended target for the `MaterialBomReference`?
