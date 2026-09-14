# Architecture Decision Overview

This document summarizes the recommended architecture decisions for the finalization of the Type III Environmental Product Declaration (EPD) Submodel. It serves as a decision package for working-group review.

| ADR | Recommended option | Confidence | Breaking impact | Working-group decision required |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-01: Lifecycle representation** | Option B (Generic Repeatable Stages with Semantic Identifiers and Aggregation Links) | High | High | Yes (Validates shift from rigid boolean boundaries to flexible semantic stages) |
| **ADR-02: Environmental Result Architecture** | Option A (One Generic Results List with a Mandatory Semantic Category) | High | High | Yes (Confirms prioritization of model semantics over physical EPD document layout) |
| **ADR-03: Result and Lifecycle Status** | Option A (Macro-Status at Module Level, Micro-Status at Indicator Level) | High | Medium | Yes (Approves the method for distinguishing missing data from calculated zeros) |
| **ADR-04: EPD Scope / Multi-Product EPDs** | Option D (Hybrid: Resolved Payload with Explicit Scope Meta-Data) | High | Low | Yes (Ensures agreement that AAS submodels contain resolved Asset values, not family calculation matrices) |
| **ADR-05: Semantic Identifier Strategy** | Option B (Controlled Working-Group Sandbox Namespace) | High | High | Yes (Requires agreement on a temporary sandbox namespace to unblock development) |
| **ADR-06: Content Declaration Architecture** | Option B (High-Level Content Summary with External References) | High | Medium | Yes (Approves the prevention of scope creep into a full Material BOM) |
| **ADR-07: Reference Units** | Option B (Common Reusable Structure with Semantic Roles for Functional and Declared Units) | High | Medium | Yes (Approves dual optional unit architecture) |
| **ADR-08: LCA Methodology and Provenance** | Option B (Strict Separation: LCAMethodology vs Provenance, removing tool-specific IDs) | High | Medium | Yes (Approves removal of specific software artefacts like ILCD UUIDs from the standard) |

**Note:** No implementations or code changes have been made. This package is strictly for working-group evaluation.
