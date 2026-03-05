---
title: "Data Setup"
---

# Data Setup

Ontop4OMOP ships with a complete set of **synthetic OMOP CDM Parquet files**
in the `data/` directory of the repository. These files represent a virtual
patient population and can be used immediately — no real patient data is
required.

---

## Repository layout

After cloning the repository you should see:

```
Ontop4OMOP/
├── data/                   ← OMOP Parquet files
│   ├── person.parquet
│   ├── visit_occurrence.parquet
│   ├── condition_occurrence.parquet
│   ├── drug_exposure.parquet
│   ├── measurement.parquet
│   ├── concept.parquet
│   └── ... (all OMOP CDM tables)
├── mappings/
│   ├── OMOP-parquet.obda   ← CLI mode mappings (reads Parquet directly)
│   ├── OMOP-duckdb.obda    ← GraphDB mode mappings (reads DuckDB views)
│   └── OMOP.properties     ← JDBC connection settings
├── ontology/
│   └── OMOP.ttl            ← OMOP OWL ontology
├── cli/                    ← CLI mode tutorial
└── graphdb-desktop/        ← GraphDB Desktop mode tutorial
```

---

## CLI mode: no database needed

In CLI mode, Ontop reads the Parquet files **directly** using DuckDB's
`read_parquet()` function embedded in the SQL queries of the mapping file.
No separate database creation step is required — just make sure the Parquet
files are present in the `data/` directory.

---

## GraphDB Desktop mode: create a DuckDB database

GraphDB's embedded Ontop requires a persistent database connection.
For this we create a DuckDB database file with SQL views over the Parquet files.

### Step 1 — Open DuckDB

```bash
duckdb db/OMOP.duckdb
```

This creates (or opens) the file `db/OMOP.duckdb`.

### Step 2 — Create tables from Parquet files

Run the following SQL. Each statement reads a Parquet file and creates a
persistent table in the DuckDB database. Execute these from the `data/`
directory, or adjust the paths accordingly.

```sql
-- Clinical tables
CREATE TABLE cdm_source AS SELECT * FROM read_parquet('cdm_source.parquet');
CREATE TABLE metadata AS SELECT * FROM read_parquet('metadata.parquet');

CREATE TABLE person AS SELECT * FROM read_parquet('person.parquet');
CREATE TABLE observation_period AS SELECT * FROM read_parquet('observation_period.parquet');
CREATE TABLE specimen AS SELECT * FROM read_parquet('specimen.parquet');
CREATE TABLE death AS SELECT * FROM read_parquet('death.parquet');

CREATE TABLE visit_occurrence AS SELECT * FROM read_parquet('visit_occurrence.parquet');
CREATE TABLE visit_detail AS SELECT * FROM read_parquet('visit_detail.parquet');

CREATE TABLE condition_occurrence AS SELECT * FROM read_parquet('condition_occurrence.parquet');
CREATE TABLE drug_exposure AS SELECT * FROM read_parquet('drug_exposure.parquet');
CREATE TABLE procedure_occurrence AS SELECT * FROM read_parquet('procedure_occurrence.parquet');
CREATE TABLE device_exposure AS SELECT * FROM read_parquet('device_exposure.parquet');
CREATE TABLE measurement AS SELECT * FROM read_parquet('measurement.parquet');
CREATE TABLE observation AS SELECT * FROM read_parquet('observation.parquet');
CREATE TABLE note AS SELECT * FROM read_parquet('note.parquet');
CREATE TABLE note_nlp AS SELECT * FROM read_parquet('note_nlp.parquet');

CREATE TABLE fact_relationship AS SELECT * FROM read_parquet('fact_relationship.parquet');

-- Administrative tables
CREATE TABLE location AS SELECT * FROM read_parquet('location.parquet');
CREATE TABLE care_site AS SELECT * FROM read_parquet('care_site.parquet');
CREATE TABLE provider AS SELECT * FROM read_parquet('provider.parquet');

CREATE TABLE payer_plan_period AS SELECT * FROM read_parquet('payer_plan_period.parquet');
CREATE TABLE cost AS SELECT * FROM read_parquet('cost.parquet');

-- Era tables
CREATE TABLE condition_era AS SELECT * FROM read_parquet('condition_era.parquet');
CREATE TABLE drug_era AS SELECT * FROM read_parquet('drug_era.parquet');
CREATE TABLE dose_era AS SELECT * FROM read_parquet('dose_era.parquet');

-- Cohort tables
CREATE TABLE cohort AS SELECT * FROM read_parquet('cohort.parquet');
CREATE TABLE relationship AS SELECT * FROM read_parquet('relationship.parquet');
CREATE TABLE cohort_definition AS SELECT * FROM read_parquet('cohort_definition.parquet');

CREATE TABLE episode AS SELECT * FROM read_parquet('episode.parquet');
CREATE TABLE episode_event AS SELECT * FROM read_parquet('episode_event.parquet');

-- Vocabulary tables
CREATE TABLE concept AS SELECT * FROM read_parquet('concept.parquet');
CREATE TABLE vocabulary AS SELECT * FROM read_parquet('vocabulary.parquet');
CREATE TABLE domain AS SELECT * FROM read_parquet('domain.parquet');
CREATE TABLE concept_class AS SELECT * FROM read_parquet('concept_class.parquet');
CREATE TABLE concept_relationship AS SELECT * FROM read_parquet('concept_relationship.parquet');
CREATE TABLE concept_synonym AS SELECT * FROM read_parquet('concept_synonym.parquet');
CREATE TABLE concept_ancestor AS SELECT * FROM read_parquet('concept_ancestor.parquet');
CREATE TABLE source_to_concept_map AS SELECT * FROM read_parquet('source_to_concept_map.parquet');
CREATE TABLE drug_strength AS SELECT * FROM read_parquet('drug_strength.parquet');
```

### Step 3 — Verify

Check that the `person` table has rows:

```sql
SELECT COUNT(*) FROM person;
```

You should see a positive count. Exit DuckDB with `.exit`.

---

## OMOP.properties

The `mappings/OMOP.properties` file tells Ontop how to connect to the database.
For CLI mode (Parquet) it uses an in-memory DuckDB connection:

```properties
jdbc.url=jdbc:duckdb:
jdbc.driver=org.duckdb.DuckDBDriver
```

For GraphDB Desktop mode, update `jdbc.url` to point to your DuckDB file:

```properties
jdbc.url=jdbc:duckdb:/absolute/path/to/db/OMOP.duckdb
jdbc.driver=org.duckdb.DuckDBDriver
```

:::{note}
Use an **absolute path** for the DuckDB file in GraphDB mode.
No OS-specific path separators are needed beyond the standard `/`.
:::
