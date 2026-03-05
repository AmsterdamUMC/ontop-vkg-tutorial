---
title: "GraphDB Desktop Mode"
---

# GraphDB Desktop Mode

In GraphDB Desktop mode, Ontop runs **embedded inside GraphDB** and connects
to a persistent DuckDB database. This gives you a full-featured triple store
interface with SPARQL, visual graph exploration, and repository management.

---

## Prerequisites

- Java 17+ installed
- GraphDB Desktop 10.x installed (see [Installation](installation.md))
- DuckDB installed and `db/OMOP.duckdb` created (see [Data Setup](data-setup.md))
- DuckDB JDBC driver placed in GraphDB's `lib/ext/` directory

---

## Step 1 — Start GraphDB Desktop

Launch GraphDB Desktop and open the Workbench at:
[http://localhost:7200](http://localhost:7200)

---

## Step 2 — Create an Ontop Virtual Repository

1. In the left sidebar, click **Setup → Repositories**
2. Click **Create new repository**
3. Select **Ontop Virtual Repository** as the repository type

Fill in the connection settings:

| Field | Value |
|-------|-------|
| **Repository ID** | `omop` (or any name you prefer) |
| **Driver class** | `org.duckdb.DuckDBDriver` |
| **JDBC URL** | `jdbc:duckdb:/absolute/path/to/db/OMOP.duckdb` |
| **Ontology** | Upload or point to `ontology/OMOP.ttl` |
| **Mapping** | Upload or point to `mappings/OMOP-duckdb.obda` |

:::{warning}
Use the **absolute path** to your `OMOP.duckdb` file in the JDBC URL.
For example: `jdbc:duckdb:/Users/yourname/projects/Ontop4OMOP/db/OMOP.duckdb`
:::

---

## Step 3 — Verify the repository

Once created, select the `omop` repository as the active repository
(top-right dropdown).

Open **SPARQL** in the left sidebar and run a test query:

```sparql
SELECT (COUNT(?p) AS ?count)
WHERE { ?p a <http://www.ohdsi.org/omop#Person> }
```

If a positive number is returned, the setup is working correctly.

---

## Step 4 — Explore the graph visually

1. In the left sidebar, click **Explore → Visual Graph**
2. In the search field, enter an IRI such as:
   ```
   http://example.org/omop/person/1
   ```
3. Click **Show** or press **Enter**

You should see the person node with its connected gender concept, year of
birth, and associated visits, conditions, and drug exposures.

---

## Step 5 — Materialize RDF (optional)

If you need a static RDF dump instead of a live virtual endpoint, you can
use the Ontop CLI to materialize the full graph:

```bash
ontop materialize \
    --mapping mappings/OMOP-duckdb.obda \
    --properties mappings/OMOP.properties \
    --output OMOP_RDF.ttl
```

Then import `OMOP_RDF.ttl` into any standard GraphDB repository via
**Import → Upload RDF files**.

---

## Architecture recap

```
OMOP Parquet files
       │
       ▼
DuckDB database (OMOP.duckdb)
       │   persistent SQL tables
       ▼
Embedded Ontop (inside GraphDB)
       │   virtual RDF mapping
       ▼
SPARQL repository :7200
```
