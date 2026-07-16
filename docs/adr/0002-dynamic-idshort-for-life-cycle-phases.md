# ADR 0002: Dynamic idShort for life-cycle phases

**Status:** Proposed for working-group review

**Initial problem:** Fixed phases limit EPDs that do not report all or report aggregated phases.
**Decision:** Derive the `idShort` dynamically from `lifeCyclePhase`.
**Examples:**
- `A1-A3` → `A1_A3`
- `B1-B7` → `B1_B7`
- `C1-C4` → `C1_C4`
**Preservation of value:** The actual technical phase value (`lifeCyclePhase`) is preserved in the dataset.
**Assignment:** Occurs **only during instantiation**.
**Uniqueness:** Unique within the respective list.
**Open question:** Handling of `Total` (see Open Design Decisions).
