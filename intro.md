---
title: "Ontop4OMOP: OMOP → SPARQL using Ontop and DuckDB"
subtitle: "A step-by-step tutorial"
date: 2026-03-03
doi: "10.5281/zenodo.XXXXXXX"

license: MIT

authors:
  - name: "Rowdy de Groot"
    orcid: "https://orcid.org/0000-0002-1248-1986"
  - name: "Andra Waagmeester"
    orcid: "https://orcid.org/0000-0001-9773-4008"

keywords:
  - OMOP CDM
  - SPARQL
  - Ontop
  - DuckDB
  - Virtual Knowledge Graph
  - FAIR data
  - Linked Data

abstract: |
  This tutorial demonstrates how to expose OMOP Common Data Model (CDM) data
  stored as Parquet files as a live SPARQL endpoint using Ontop and DuckDB.
  No RDF materialization is required. Two deployment modes are covered:
  the standalone Ontop CLI and GraphDB Desktop with embedded Ontop.
---

# Ontop4OMOP Tutorial

This tutorial walks you through **Ontop4OMOP** — a cross-platform, reproducible
setup for exposing [OMOP CDM](https://www.ohdsi.org/data-standardization/) data
as a SPARQL endpoint using:

- **DuckDB** — an embedded analytical database that reads Parquet files directly
- **Ontop** — a Virtual Knowledge Graph (VKG) system that maps SQL to RDF on the fly
- **OBDA mappings** — declarative rules that translate SQL results into RDF triples

## What you will learn

By the end of this tutorial you will be able to:

1. Install the required software (Java, Ontop CLI, DuckDB)
2. Set up a DuckDB database from OMOP Parquet files
3. Understand the OBDA mapping files that define the OMOP ontology
4. Start a live SPARQL endpoint with the Ontop CLI
5. Connect GraphDB Desktop to the same data via an Ontop Virtual Repository
6. Run example SPARQL queries over OMOP data

## Architecture

The data pipeline looks like this:

```
OMOP Parquet files  →  DuckDB (embedded)  →  Ontop  →  SPARQL endpoint
```

Two deployment modes are supported:

**CLI mode** — lightweight, no GUI required:

```
OMOP Parquet files  →  Ontop CLI  →  SPARQL endpoint :8081
```

**GraphDB Desktop mode** — uses persistent SQL views:

```
OMOP Parquet files  →  DuckDB database  →  persistent SQL views  →  embedded Ontop in GraphDB  →  SPARQL repository :7200
```

## Source repository

The full source code is available at:
[https://github.com/AmsterdamUMC/Ontop4OMOP](https://github.com/AmsterdamUMC/Ontop4OMOP)

```{tableofcontents}
```
