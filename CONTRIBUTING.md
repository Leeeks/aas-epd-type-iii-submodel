# Contributing

## Process
1. Create a GitHub Issue.
2. Name the affected AAS path.
3. Describe the current modeling.
4. Describe the proposed change.
5. Provide a technical justification.
6. Cite a normative or program-related source.
7. Evaluate the impact on compatibility.
8. Update the template.
9. Update the example instance.
10. Update the documentation and changelog.
11. Create a Pull Request for working-group review.

## Rules
- `idShort`: No spaces, avoid dynamic values, stay compliant with standards.
- `displayName`: Clear and preferably in English.
- `semanticId`: Must be maintained, references standards.
- `ConceptDescriptions`: Must not be missing for Submodel Elements.
- `Collections` and `Lists`: Use appropriately according to cardinality.
- `List elements`: Without static instance-specific `idShort`.
- `Units`: Correct specification in the `characterizationUnit`.
- `File names`: lowercase-kebab-case, no spaces/umlauts/special characters (except hyphens), no internal iterations.
- `Versioning`: Version increments are done consciously.
- `Breaking Changes`: Must be marked as such.
