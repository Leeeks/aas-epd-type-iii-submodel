# ADR-07: Functional Unit and Declared Unit

## Context

In Life Cycle Assessment (LCA) and EPDs, the reference unit by which all environmental impacts are scaled is either a "Functional Unit" or a "Declared Unit". A Functional Unit describes the quantified performance of a product system (e.g., "lighting 10 square meters for 50,000 hours"). A Declared Unit is used when the exact function is unknown or for intermediate products (e.g., "1 kilogram of cement"). These are distinct, often mutually exclusive concepts depending on the PCR, but structurally they share the same data requirements (quantity, unit of measure, description).

## Source constraints

* PEP Ecopassport mandates the use of a Functional Unit for electrical goods but permits a Declared Unit in specific edge cases.
* EPD International generally uses a Functional Unit but mandates a Declared Unit for intermediate products (like raw materials).
* Both concepts are valid EPD reference units. Neither can be made universally mandatory at the AAS schema level because their applicability depends entirely on the product type and PCR.

## Requirements

The chosen architecture must:
* Maintain the semantic distinction between a Functional Unit and a Declared Unit.
* Design a common, reusable structural model to prevent duplicating the internal fields (quantity, unit, description, reference service life, mass conversion).
* Ensure both `FunctionalUnit [0..1]` and `DeclaredUnit [0..1]` are available in the schema.

## Option A

**Separate, Duplicated Structures**

Structure: Create two entirely separate SMLs (`FunctionalUnit` and `DeclaredUnit`), and manually duplicate properties like `quantity`, `unitId`, and `description` inside each.

**Advantages:**
* Explicit distinction in the schema.

**Disadvantages:**
* High structural duplication.
* Harder to maintain if new properties (like conversion factors) are added later.

## Option B

**Common Reusable Structure with Semantic Roles**

Structure: Define a reusable structure (e.g., a "ReferenceUnit" SMC pattern) that contains `quantity`, `unit`, `description`, `massConversionFactor`, and `referenceServiceLife`. Instantiate this structure twice in the EPD Submodel: once as `FunctionalUnit [0..1]` and once as `DeclaredUnit [0..1]`.

Example AAS hierarchy:
```
EPD Submodel
├── FunctionalUnit [0..1] (Instance of ReferenceUnit structure)
│   ├── Quantity: 1
│   ├── Unit: "piece" (SemanticId)
│   ├── Description: "One router operating for 10 years"
│   └── ReferenceServiceLife: 10
└── DeclaredUnit [0..1] (Instance of ReferenceUnit structure)
    ├── Quantity: 1
    ├── Unit: "kg" (SemanticId)
    └── MassConversionFactor: 1.0
```

**Advantages:**
* DRY (Don't Repeat Yourself) data modeling.
* Retains strict semantic distinction at the top level of the Submodel.
* Allows PCR-specific validation rules to easily check if the correct unit type was provided.

**Disadvantages:**
* None significant.

## Recommendation

**Option B** is recommended. Both `FunctionalUnit` and `DeclaredUnit` must exist as optional (`0..1`) concepts at the root of the EPD Submodel to respect the varying source constraints of different PCRs. By using a common reusable structure for both, we ensure consistency in how quantities and units are expressed while preserving their vital semantic distinction.

## Consequences

* **What becomes easier:** Parsing the reference unit. Consumers can write one parsing function for "ReferenceUnit" and apply it to whichever unit type is populated.
* **What becomes harder:** Nothing.

## Programme compatibility

* **PEP ecopassport:** Compatible. Will populate `FunctionalUnit`.
* **EPD International non-construction:** Compatible. Will populate `FunctionalUnit` or `DeclaredUnit` based on product type.
* **EPD International construction / EN 15804:** Compatible. Will populate `DeclaredUnit` (or `FunctionalUnit` if assessing a whole building/system).

## Downstream consumer perspective

Consumers will check which unit is populated (Functional or Declared). They will use this information to understand exactly what the LCA results represent (e.g., dividing the results by the `quantity` to get a per-unit footprint). The consistent internal structure makes it easy to extract the multiplier and unit of measure.

## Breaking change impact

* **Medium**. Replaces any existing single-unit assumption with the dual optional structure, necessitating an update to how the reference quantity is queried.

## Open questions

* Should the schema enforce a constraint that *at least one* of the two units must be provided? (Generally yes, an EPD without a reference unit is mathematically meaningless).
