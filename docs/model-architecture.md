# Model Architecture

This document describes the conceptual architecture of the EPD Type III Submodel.

## Repository conventions
This repository follows typical conventions of the IDTA and `admin-shell-io` repositories for Submodel Templates:
- Provision of a generic `.aasx` template file under `model/template`.
- Provision of concrete instantiation examples under `examples/`.
- Structured decision making through Architecture Decision Records (ADRs) under `docs/adr/`.
- Issues and Pull Request Templates for structured collaboration.

## Structure of the model
The EPD Submodel is divided into logical groups:
- Product identification and EPD metadata.
- Functional and Declared Unit.
- Life cycle phases.
- LCIA results (environmental impacts, resource use, waste categories, output flows).
- References to normative documents (PCR, PSR).
