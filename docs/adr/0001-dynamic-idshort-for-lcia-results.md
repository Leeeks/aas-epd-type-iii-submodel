# ADR 0001: Dynamic idShort for LCIA results

**Status:** Proposed for working-group review

**Initial problem:** Direct list elements were displayed as `Unknown`. Fixed `idShort` per indicator restricted extensibility.
**Decision:** Derive the `idShort` dynamically from the `indicatorCode` during instantiation.
**Example:** `GWP-total` is converted to `GWP_total`.
**Normalization rules:** Replace hyphens and spaces with underscores. Remove special characters.
**Uniqueness:** In the case of naming conflicts, it is ensured that the list remains consistent, as indicators are unique per list.
**Assignment:** Occurs **only during instantiation**.
**Advantage:** The generic template remains indicator-independent.
**Dependency:** Dependent on the AAS metamodel version (handling of lists).
