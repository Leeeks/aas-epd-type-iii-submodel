# EPD Submodel Architecture Refactoring Migration Guide

## Overview

This guide details the structural changes made to the AAS EPD Type III Submodel template to align with the new model semantics and to resolve architectural issues outlined in the Architecture Decision Records (ADRs).

## Key Structural Changes

### 1. System Boundaries and LCAMethodology
- **Removed**: The root-level `systemBoundary` SubmodelElementCollection (and its boolean flags like `includesA1_A3`).
- **Removed**: The `representativenessReference` collection.
- **Added**: `LCAMethodology` [SMC] which absorbs legitimate methodological parameters (e.g. reference year).
- **Added**: `DeclaredStages` [SML] inside `LCAMethodology`, containing a list of `StageDeclaration` [SMC] elements. Each specifies the `stageCode` and `stageStatus` (e.g., Assessed, NotAssessed).

### 2. Environmental Results
- **Removed**: `lciaResults` [SML].
- **Added**: `EnvironmentalResults` [SML], designed to house all indicator types in a unified schema structure.
- **Added**: Inside `EnvironmentalResults`, `EnvironmentalResult` [SMC] specifies the `resultCategory` (e.g., `ImpactIndicator`, `ResourceUse`, `Waste`, `OutputFlow`), `indicatorCode`, and a nested `stageValues` list.
- **Impact on Mapping**: Tools must map original results to `EnvironmentalResult` by explicitly categorizing the indicator. 

### 3. EPD Scope Definition
- **Added**: `EPDScope` [SMC] at the root level.
- **Added**: `scopeType` (Instance, Type, Family), `coveredProductReferences`, and `scopeDescription` provide explicit context for what the environmental impacts apply to, resolving the single vs. family representation ambiguity.

### 4. Content Declaration
- **Added**: `ContentDeclaration` [SMC] provides LCA-relevant summary metrics (`productMass`, `recycledContentPercentage`, `biogenicCarbonContentProduct`) decoupled from the general manufacturer BOM, supporting specific end-of-life calculations.

### 5. Reference Units Unified
- **Modified**: Both `DeclaredUnit` and `FunctionalUnit` now use a standard sub-structure requiring `quantity` (xs:decimal) and `unit` (xs:string), ensuring numeric parsability instead of arbitrary string descriptions.

### 6. Semantic Identifier Draft Namespace
- **Modified**: Elements lacking official ECLASS or IDTA semantic identifiers have been migrated from placeholder domains (e.g. `example.com`) to the provisional `https://wg-epd.example.com/draft/v1/` namespace to explicitly flag them for future standardization.

## Example Migration

The included WAGO PEP example (`examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx`) has been fully migrated to demonstrate compliance with this new structure, effectively separating the semantic meaning of the results from the constraints of the PEP document structure.
