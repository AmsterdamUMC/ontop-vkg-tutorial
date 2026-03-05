---
title: "Virtual Knowledge Graphs with Ontop"
subtitle: "SWAT4HCLS 2026 Tutorial"
date: 2026-03-05
doi: "10.5281/zenodo.XXXXXXX"

license: MIT

authors:
  - name: "Carsten Fortmann-Grote"
    orcid: "https://orcid.org/0000-0002-2579-5546"
  - name: "Rowdy de Groot"
    orcid: "https://orcid.org/0000-0002-1248-1986"
  - name: "Andra Waagmeester"
    orcid: "https://orcid.org/0000-0001-9773-4008"

keywords:
  - Virtual Knowledge Graph
  - Ontop
  - OBDA
  - SPARQL
  - RDF
  - OMOP CDM
  - GBIF
  - OMERO
  - DuckDB
  - PostgreSQL
  - FAIR data
  - Linked Data

abstract: |
  This tutorial introduces Virtual Knowledge Graphs (VKGs) using the Ontop
  framework. Starting from a solar system dataset, you will learn how to
  convert tabular data to RDF, write OBDA mappings, and launch SPARQL
  endpoints over relational databases — without materializing any RDF.
  The core concepts are then applied to real-world use cases in clinical
  data (OMOP CDM), biodiversity (GBIF), and bioimaging (OMERO).
---

# Virtual Knowledge Graphs with Ontop

This tutorial introduces **Virtual Knowledge Graphs (VKGs)** — a technique
for exposing relational data as RDF through a live SPARQL endpoint, without
copying or converting the data. The mapping is purely virtual: every SPARQL
query is translated to SQL on the fly.

The tutorial is built around the [Ontop](https://ontop-vkg.org/) VKG framework
and uses the **Ontology-Based Data Access (OBDA)** mapping language.

## Tutorial structure

The tutorial is organised in three parts:

### Part I — Core concepts

1. **Warmup** — Convert a CSV table of planets to RDF using Python and rdflib.
   Understand the relationship between wide/long tables and RDF triples.
2. **OBDA Mappings** — Learn the Ontop mapping language by virtualising
   a solar system PostgreSQL database (planets and moons).
3. **Installation** — Set up Java, Ontop CLI, DuckDB, and optionally
   PostgreSQL and GraphDB Desktop.

### Part II — Use case demonstrators

4. **OMOP CDM** — Expose clinical OMOP data stored as Parquet files via
   DuckDB and Ontop.
5. **GBIF Biodiversity** — Query GBIF occurrence records from S3 Parquet
   snapshots through a SPARQL endpoint.

### Part III — Advanced application

6. **OMERO Bioimaging** — Apply Ontop to an OMERO PostgreSQL database to
   virtualise microscopy image metadata.

## Architecture

The general VKG pipeline:

```
Relational data  →  Ontop (OBDA mappings + ontology)  →  SPARQL endpoint
```

Ontop supports any JDBC-accessible database. This tutorial demonstrates
three backends:

| Backend    | Use case         | Data format               |
|------------|------------------|---------------------------|
| PostgreSQL | Solar system, OMERO | Tables in a SQL database |
| DuckDB     | OMOP CDM         | Parquet files (embedded)  |
| DuckDB     | GBIF             | Parquet files (from S3)   |

## Source repositories

- **This tutorial**: [AmsterdamUMC/Ontop4OMOP-book](https://github.com/AmsterdamUMC/Ontop4OMOP-book)
- **SWAT4HCLS materials**: [mpievolbio-scicomp/swat4hcls2026-ontop-tutorial](https://gitlab.gwdg.de/mpievolbio-scicomp/swat4hcls2026-ontop-tutorial)
- **OMOP source**: [AmsterdamUMC/Ontop4OMOP](https://github.com/AmsterdamUMC/Ontop4OMOP)
- **OMERO mappings**: [German-BioImaging/omero-ontop-mappings](https://github.com/German-BioImaging/omero-ontop-mappings)

```{tableofcontents}
```
