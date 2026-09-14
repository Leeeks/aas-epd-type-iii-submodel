# ADR-03: Result and Lifecycle Status

## Context

EPD data structures must precisely communicate missing, irrelevant, or zero values. A calculated numeric impact value of precisely `0.0` is fundamentally different from a stage that is "Not Declared" (ND), or a module that is "Not Relevant" / "Module Not Relevant" (MNR). Simply omitting a value in an array is ambiguous, as it could imply zero, missing data, or an error in parsing. The architecture must formally distinguish between the status of an overarching lifecycle stage, the status of a specific indicator result, and valid numeric zero values.

## Source constraints

* EN 15804 and EPD International explicitly use designations like "ND" (Not Declared) in result cells where data was not assessed.
* For system boundaries, programs define states like MND (Module Not Declared), MNR (Module Not Relevant).
* PEP Ecopassport uses similar concepts (exclusions, Not Applicable).
* `xs:decimal` and other numeric types cannot store string values like "ND".

## Requirements

The chosen architecture must:
* Distinguish the status of a lifecycle stage/module in the boundary declaration from the status of an individual indicator result.
* Provide a mechanism to declare a value as genuinely zero.
* Map program-specific codes (MND, MNR, Excluded) to generic machine-readable states.
* Preserve the original programme-specific source codes if they provide useful provenance.

## Option A

**Macro-Status at Module Level, Micro-Status at Indicator Level**

Structure: A required generic `Status` enum at the Lifecycle Stage definition (from ADR-01) mapping to macro states (Declared, Not Assessed, Not Relevant). A secondary, optional `IndicatorStatus` at the individual result cell level to handle granular exceptions (e.g., an entire module is Declared, but one specific flow within it is Not Declared). If the `IndicatorStatus` indicates missing data, the numeric value field is omitted. Original codes are kept as optional strings.

Example AAS hierarchy:
```
EPD Submodel
├── LifecycleStages
│   └── A1
│       ├── Status: "Declared"
│       └── OriginalStatusCode: "MND" (Optional provenance string)
└── EnvironmentalResults
    └── GlobalWarmingPotential
        └── Values
            └── A1
                ├── IndicatorStatus: "NotAssessed"
                └── OriginalStatusCode: "ND"
```

**Advantages:**
* Strongly typed numeric fields are preserved because strings like "ND" are moved to dedicated status properties.
* Prevents ambiguity: a zero is a calculated zero, while a missing value with `IndicatorStatus="NotAssessed"` means data is absent.
* Maps elegantly to the conceptual separation between system boundaries (macro) and individual table cells (micro).
* Preserves original provenance strings for auditing.

**Disadvantages:**
* Increases verbosity of the resulting AAS payload.

## Option B

**String Typing for All Result Values**

Structure: Change the fundamental data type of result values from decimal/float to strings. This allows publishing `"0.0"`, `"ND"`, `"MNA"`, directly in the value field.

**Advantages:**
* Extremely simple.
* Perfectly mirrors what is visually printed in an EPD table.

**Disadvantages:**
* Violates basic data modeling principles.
* Breaks downstream computational tools, which must now parse strings to perform LCA aggregations, risking runtime errors.
* Mixes metadata (status) with payload data (value).

## Recommendation

**Option A** is recommended. The separation of concerns (status vs value) is critical for machine-readable data. Option A supports generic conceptual states (Declared, Not Assessed, Not Relevant) that work across all EPD programs while providing optional string fields to retain program-specific acronyms for provenance.

## Consequences

* **What becomes easier:** Automated calculation engines can safely process numeric fields without crashing on strings. Zeroes are treated accurately as mathematically valid results.
* **What becomes harder:** The JSON/XML payload for an AAS becomes slightly more verbose.

## Programme compatibility

* **PEP ecopassport:** Compatible. "Not Applicable" maps to "NotRelevant".
* **EPD International non-construction:** Compatible. "ND" maps to "NotAssessed".
* **EPD International construction / EN 15804:** Compatible. "MND" and "MNR" map to generic macro states, while their string values can be preserved for exact provenance.

## Downstream consumer perspective

Consumers will first check the `Status` or `IndicatorStatus`. If it is "NotAssessed" or "NotRelevant", they know they should not expect a numeric value and can halt calculations or flag missing data to the user. If the status is "Declared", they can safely consume the numeric value, knowing a `0.0` is an actual calculated finding.

## Breaking change impact

* **Medium**. Requires replacing existing null-handling or implicit assumptions with explicit enum status flags across stage declarations and result cells.

## Open questions

* Should the generic states (Declared, Not Assessed, Not Relevant) be strictly defined as a standard IDTA enumeration?
