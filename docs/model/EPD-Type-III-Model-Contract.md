# EPD Type III Model Architecture Contract

This document defines the invariants, boundaries, and required architectures of the EPD Type III Submodel.

## 1. Property Name and Structure Invariants

### 1.1 EnvironmentalResult Architecture
The `EnvironmentalResult` structure has been intentionally flattened compared to historical EPD models. The `unit` property at the `EnvironmentalResult` level **must** be preserved as the characterization unit. It must NOT be replaced by or nested into a `characterizationUnit` SubmodelElementCollection.

**Required Elements:**
- `resultCategory` (Property, String)
- `indicatorCode` (Property, String)
- `indicatorName` (Property, String)
- `unit` (Property, String) - The characterization unit.
- `unitId` (Property, String) - The semantic ID of the characterization unit.
- `stageValues` (SubmodelElementList) - The assessed lifecycle values.

**Optional Extensions (Semantics restored):**
- `baseUnit` (SubmodelElementCollection) - When the characterization unit represents a complex derived unit, the underlying physical base unit MUST be provided using this SMC. It must contain:
  - `unit` (Property, String)
  - `unitId` (Property, String)

## 2. Vocabulary Invariants

### 2.1 Environmental Indicator Registry
The `environmental-indicator-registry.yaml` is the single source of truth for indicator and unit mapping.

- Validation systems MUST enforce that any combination of `indicatorCode` + `unit` matches an entry in this registry.
- Users MUST NOT use arbitrary indicator codes unless following the explicit extension rules.

### 2.2 Extension Rules
Extensions to closed vocabularies are permitted only when practically necessary (e.g. PCR-specific indicators not listed in the registry).
- Extended properties MUST still respect the expected data types.
- Extended indicators MUST include an explicit `unit` and `unitId`.

### 2.3 Semantic Provisioning
All model components must use the `wg-epd.example.com` or officially recognized IDs (such as `admin-shell.io`). You must not fabricate semantic IDs. Unofficial IDs must be explicitly marked as provisional (e.g. `https://wg-epd.example.com/draft/v1/...`).

## 3. IEC 61360 ValueLists

The template provides IEC 61360 ValueLists for closed or strongly-typed vocabularies:
- `indicatorCode`
- `stageCode`
- `resultCategory`
- `stageStatus`
- `valueStatus`
- `scopeType`
- `siteType`

These ValueLists act as the primary machine-readable reference for allowable enumerations. Every `valueId` reference in these ValueLists MUST point to a valid, instantiated `ConceptDescription` within the model to prevent dangling references.

## 4. Submodel Specific Invariants

### 4.1 LCAMethodology
The `LCAMethodology` structure is strictly defined. Legacy properties from earlier models (e.g., `referenceFlow.id`, `referenceFlow.amount`, `pictogramSource`, `flowDiagramSource`, `dataSetValidUntil`, `technicalPurpose`) MUST NOT be present. The property `referenceYear` MUST be named `lcaReferenceYear`. The property `location` MUST be named `geographicalScope`. The property `energyModel` MUST be named `lcaEnergyModel`.

### 4.2 ContentDeclaration
The `ContentDeclaration` structure MUST represent biogenic carbon using a single, properly nested SMC named `biogenicCarbonContent`. It MUST contain the properties `biogenicCarbonContentProduct` and `biogenicCarbonContentPackaging`. Flat representations or duplicates within `manufacturerProduct` MUST NOT be present.

### 4.3 EPDScope
The `EPDScope` SMC MUST NOT contain the redundant property `sourceDeclarationReference`. Declarations are identified purely by the `identificationPublication` fields. 
