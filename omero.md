---
title: "OMERO Virtualization"
---

# OMERO Virtualization

[OMERO](https://www.openmicroscopy.org/omero/) (Open Microscopy Environment
Remote Objects) is a widely used platform for managing bioimaging data. Its
PostgreSQL database stores rich metadata about images, experiments, and
annotations — making it an ideal candidate for virtualization with Ontop.

This chapter applies the same OBDA mapping approach from the solar system
exercise to a real-world OMERO installation.

---

## Overview

The OMERO data model includes tables such as:

- `image` — microscopy images with acquisition metadata
- `experimenter` — users/researchers
- `experimentergroup` — research groups
- `screen`, `plate`, `well`, `plateacquisition` — high-content screening data
- `roi`, `channel`, `pixels` — image regions and channels
- `annotation_mapvalue` — key-value annotations attached to images

The full OMERO data model is documented at:
[OME Model Overview](https://ome-model.readthedocs.io/en/stable/developers/model-overview.html)

---

## Prerequisites

- Ontop CLI installed (see [Installation](installation.md))
- PostgreSQL JDBC driver in your Ontop `jdbc/` directory
- Access to an OMERO PostgreSQL database (the tutorial provides a shared
  test instance, or you can use your own)

---

## Step 1 — Clone the OMERO mappings repository

The [omero-ontop-mappings](https://github.com/German-BioImaging/omero-ontop-mappings)
repository contains starter OBDA mappings for OMERO:

```bash
git clone https://github.com/German-BioImaging/omero-ontop-mappings -b swat4hcls2026
cd omero-ontop-mappings
```

### Install Ontop CLI (if not already installed)

The repo includes a convenience script:

```bash
bash utils/install_ontop.sh
```

Verify the installation:

```bash
ontop-cli/ontop help
```

---

## Step 2 — Explore the OMERO database

Useful SQL queries for understanding the database while writing mappings:

### List all tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE NOT starts_with(table_name, 'pg_');
```

### List columns in a table

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'image';
```

The `image` table contains columns such as:

| column_name        |
|--------------------|
| id                 |
| acquisitiondate    |
| description        |
| name               |
| owner_id           |
| group_id           |
| instrument         |
| fileset            |
| ...                |

---

## Step 3 — Launch the Ontop endpoint

The repository contains pre-configured artifacts in the `omeswat/` directory:

```bash
cd omeswat
./omeswat-ontop-endpoint.sh --dev
```

The log should end with:

```
-INFO  in i.u.i.o.e.OntopEndpointApplication - Started OntopEndpointApplication
```

Navigate to [http://localhost:8080](http://localhost:8080) to access the
Ontop SPARQL query interface.

---

## Step 4 — Explore the existing mappings

The mappings in `omeswat/omeswat.obda` provide a minimal starting point.
The Ontop query UI includes several tabs with pre-written queries:

- **Playground** — free-form SPARQL queries
- **Basic Queries** — simple retrieval queries
- **Tests** — `ASK` queries that validate your mappings

Run the test queries to verify the endpoint is working. All `ASK` queries
should return `true`.

---

## Assignments

The provided mappings are intentionally minimal. Extend them with the
following tasks:

### Assignment 1: Add entity mappings

Create mappings (similar to the `image-id` mapping) for:

- `experimenter`
- `experimentergroup`
- `screen`
- `well`
- `plate`
- `plateacquisition`
- `roi`
- `channel`
- `pixels`

Each mapping should:
1. Define a class for the entity (e.g. `:Experimenter a owl:Class`)
2. Map the `id` and `name` columns (where available)
3. Add the class and property declarations to the ontology

### Assignment 2: Map annotations

Create a mapping that exposes image map annotations. OMERO stores key-value
annotations in the `annotation_mapvalue` table. Your mapping should:

- Create blank nodes for each annotation entry
- Add `:key` and `:value` properties
- Link the annotation to its parent image

:::{hint}
This requires a JOIN between the annotation tables and the image table.
Use `information_schema.columns` queries to discover the relevant foreign
key relationships.
:::

### Assignment 3: Write your own mapping

Choose an aspect of the OMERO data model that interests you and create a
new mapping from scratch. Consider:

- Linking images to their pixel dimensions
- Mapping ROI (Region of Interest) coordinates
- Exposing instrument and objective metadata

---

## Connection to the solar system exercise

Notice how the same three Ontop artifacts appear in both use cases:

| File | Solar system | OMERO |
|------|-------------|-------|
| `.properties` | `solar_system.properties` | `omeswat.properties` |
| `.obda` | `solar_system.obda` | `omeswat.obda` |
| `.ttl` | `solar_system.ttl` | `omeswat.ttl` |

The pattern is always the same:

```
SQL database  →  .properties (connection)
              →  .obda (mappings)
              →  .ttl (ontology)
              →  Ontop endpoint  →  SPARQL
```

Whether you are mapping 8 planets or thousands of microscopy images, the
workflow is identical. Only the SQL queries and RDF templates change.
