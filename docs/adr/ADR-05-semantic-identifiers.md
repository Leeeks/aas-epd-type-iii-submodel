# ADR-05: Semantic Identifier Strategy

## Context

The Asset Administration Shell relies heavily on global semantic identifiers (URIs/IRIs) to provide machine-readable meaning to data structures. Currently, the draft model uses placeholder URLs (e.g., `http://example.com/...` or unilaterally invented `https://admin-shell.io/sandbox/...`). This violates IDTA guidelines for official submodels and breaks machine resolution. However, we cannot unilaterally mint official IDTA identifiers before the standard is finalized. We must define a safe development-stage strategy that distinguishes provisional identifiers from official, published semantic identifiers.

## Source constraints

* IDTA requires valid, resolvable URIs for published models.
* `admin-shell.io` is controlled by the IDTA; working groups cannot assume arbitrary paths are available for unilateral use.
* Semantic IDs define the interoperability of the submodel.

## Requirements

The chosen architecture must:
* Provide a safe namespace for draft/development work.
* Establish a clear migration path to official IDTA identifiers.
* Maximize the use of existing, stable external dictionaries (e.g., eCl@ss, EPD International glossaries) where applicable to reduce the number of new IDs needed.
* Clearly distinguish between provisional and official semantic identifiers in the documentation and schemas.

## Option A

**Wait for Official IDTA Allocation**

Structure: Halt semantic binding until official IDTA URIs are granted.

**Advantages:**
* Prevents the proliferation of "temporary" IDs that might accidentally leak into production.

**Disadvantages:**
* Completely blocks development, testing, and validation of the AAS model, as validation tools will reject models lacking proper semantic bindings.

## Option B

**Controlled Working-Group Sandbox Namespace**

Structure: Define an explicit sandbox namespace controlled by the working group (or an agreed-upon draft path) specifically designed to be easily regex-replaced later. For example: `https://wg-epd.example.com/draft/v1/...` or a designated IDTA draft namespace if granted. Maximize reliance on external dictionaries for generic terms (like units of measure).

**Advantages:**
* Unblocks development and testing.
* Clearly signals to users and reviewers that the identifiers are provisional.
* Easy to migrate to official IDs via text replacement before final publication.

**Disadvantages:**
* Temporary IDs still technically exist in draft documents.

## Recommendation

**Option B** is recommended. The architecture must clearly distinguish provisional identifiers from official published semantic identifiers. By establishing a strictly controlled, explicitly "draft" namespace for internal model concepts, development can proceed. We must also aggressively map to external semantic dictionaries (eCl@ss) wherever possible to reduce the burden of minting new IDs. When the submodel is finalized, the draft namespace will be globally replaced with the official IDTA URIs.

## Consequences

* **What becomes easier:** Rapid prototyping, validation of the JSON/XML structures, and implementation of proof-of-concept parsers.
* **What becomes harder:** Ensuring that no draft IDs accidentally survive into the final published specification.

## Programme compatibility

* **PEP ecopassport:** Compatible. (Semantic IDs are an AAS construct).
* **EPD International non-construction:** Compatible.
* **EPD International construction / EN 15804:** Compatible.

## Downstream consumer perspective

Consumers participating in the draft review phase must be aware that the semantic IDs are subject to change. They should design their software to allow easy updates of the base URI for the semantic concepts once the standard is published.

## Breaking change impact

* **High**. Changing semantic IDs breaks all existing downstream parsing logic that relies on them. However, since the model is currently in draft, this breakage is expected and necessary.

## Open questions

* Can the IDTA provide an official "sandbox" or "draft" namespace for working groups to use during development to avoid using third-party domains?
