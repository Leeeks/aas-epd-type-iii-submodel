# ADR 0003: LCIA characterization unit model

**Status:** Proposed for working-group review

**Decision:** Compact modeling of the LCIA unit.

**Structure:**
```text
characterizationUnit
├── unit
├── unitId
└── baseUnit [optional]
    ├── unit
    └── unitId
```

**Explanation:**
- `characterizationUnit.unit` designates the full LCIA unit (e.g., kg CO2-eq).
- `characterizationUnit.unitId` identifies the full LCIA unit.
- `baseUnit` is only an optional physical base unit (e.g., kg).
- An ECLASS base unit **does not** replace the full LCIA unit.
- Custom LCIA unit IDs can still be working IDs until they are standardized.
- Unverified ECLASS IRDIs must not be used.
- `unit` and `unitId` may have the same name in different collections.
