---
title: "Use Case: OMOP Clinical Data"
---

# Use Case: OMOP Clinical Data

The [OMOP Common Data Model (CDM)](https://www.ohdsi.org/data-standardization/)
is a widely used standard for observational health data. This chapter
demonstrates how to expose OMOP CDM data stored as **Parquet files** as a
SPARQL endpoint using Ontop and DuckDB — applying the same VKG principles
from the core tutorial.

:::{note}
This use case uses **DuckDB** (an embedded analytical database) instead of
PostgreSQL. DuckDB can read Parquet files directly via `read_parquet()`,
making it ideal for file-based datasets.
:::

---

## Prerequisites

- Java 17+ and Ontop CLI installed (see [Installation](installation.md))
- DuckDB installed
- DuckDB JDBC driver in the Ontop `jdbc/` directory

---

## Step 1 — Get the data

Clone the Ontop4OMOP repository:

```bash
git clone https://github.com/AmsterdamUMC/Ontop4OMOP.git
cd Ontop4OMOP
```

The repository contains synthetic OMOP Parquet files in the `data/`
directory:

```
Ontop4OMOP/
├── data/                   ← OMOP Parquet files
│   ├── person.parquet
│   ├── visit_occurrence.parquet
│   ├── condition_occurrence.parquet
│   ├── drug_exposure.parquet
│   ├── measurement.parquet
│   ├── concept.parquet
│   └── ...
├── mappings/
│   ├── OMOP-parquet.obda   ← CLI mode mappings
│   ├── OMOP-duckdb.obda    ← GraphDB mode mappings
│   └── OMOP.properties     ← JDBC connection
└── ontology/
    └── OMOP.ttl            ← OMOP OWL ontology
```

---

## Step 2 — Understand the mappings

The OBDA mapping file (`OMOP-parquet.obda`) maps OMOP tables to RDF using
the same `source`/`target` pattern from the solar system exercise. Here the
SQL source queries use DuckDB's `read_parquet()` function:

### Person mapping

```
mappingId      person_class
target         ex:person/{person_id} a omop:Person .
source         SELECT person_id FROM read_parquet('person.parquet')

mappingId      person_gender
target         ex:person/{person_id} omop:hasGenderConcept ex:concept/{gender_concept_id} .
source         SELECT person_id, gender_concept_id FROM read_parquet('person.parquet')

mappingId      person_birth
target         ex:person/{person_id} omop:yearOfBirth "{year_of_birth}"^^xsd:gYear .
source         SELECT person_id, year_of_birth FROM read_parquet('person.parquet')
```

### Visit, Condition, Drug, Measurement mappings

The same pattern applies to all OMOP domains:

| Domain | IRI pattern | Source |
|--------|------------|--------|
| Visit | `ex:visit/{visit_occurrence_id}` | `visit_occurrence.parquet` |
| Condition | `ex:condition/{condition_occurrence_id}` | `condition_occurrence.parquet` |
| Drug | `ex:drug/{drug_exposure_id}` | `drug_exposure.parquet` |
| Measurement | `ex:measurement/{measurement_id}` | `measurement.parquet` |

---

## Step 3 — Connection properties

The `OMOP.properties` file uses an in-memory DuckDB connection:

```properties
jdbc.url=jdbc:duckdb:
jdbc.driver=org.duckdb.DuckDBDriver
```

---

## Step 4 — Start the SPARQL endpoint

From the repository root:

```bash
ontop endpoint \
    --ontology ontology/OMOP.ttl \
    --mapping mappings/OMOP-parquet.obda \
    --properties mappings/OMOP.properties \
    --port=8081
```

Open [http://localhost:8081](http://localhost:8081) to access the Ontop
SPARQL workbench.

---

## Example SPARQL queries

### Count all persons

```sparql
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT (COUNT(?p) AS ?count)
WHERE {
  ?p a omop:Person .
}
```

### Persons with gender and birth year

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?person ?genderConcept ?birthYear
WHERE {
  ?person a omop:Person .
  OPTIONAL { ?person omop:hasGenderConcept ?genderConcept . }
  OPTIONAL { ?person omop:yearOfBirth ?birthYear . }
}
LIMIT 20
```

### Count conditions per person

```sparql
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?person (COUNT(?condition) AS ?conditionCount)
WHERE {
  ?condition a omop:ConditionOccurrence .
  ?condition omop:person ?person .
}
GROUP BY ?person
ORDER BY DESC(?conditionCount)
LIMIT 20
```

### All clinical facts for one person

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?type ?fact
WHERE {
  {
    ?fact a omop:VisitOccurrence .
    BIND("Visit" AS ?type)
  } UNION {
    ?fact a omop:ConditionOccurrence .
    BIND("Condition" AS ?type)
  } UNION {
    ?fact a omop:DrugExposure .
    BIND("Drug" AS ?type)
  } UNION {
    ?fact a omop:Measurement .
    BIND("Measurement" AS ?type)
  }
  ?fact omop:person ex:person/1 .
}
ORDER BY ?type
```

---

## Optional: GraphDB Desktop mode

GraphDB Desktop can host the same OMOP data using its embedded Ontop.
This requires a persistent DuckDB database file instead of reading
Parquet files on the fly.

### Create the DuckDB database

```bash
duckdb db/OMOP.duckdb
```

Then create tables from each Parquet file:

```sql
CREATE TABLE person AS SELECT * FROM read_parquet('data/person.parquet');
CREATE TABLE visit_occurrence AS SELECT * FROM read_parquet('data/visit_occurrence.parquet');
CREATE TABLE condition_occurrence AS SELECT * FROM read_parquet('data/condition_occurrence.parquet');
CREATE TABLE drug_exposure AS SELECT * FROM read_parquet('data/drug_exposure.parquet');
CREATE TABLE measurement AS SELECT * FROM read_parquet('data/measurement.parquet');
CREATE TABLE concept AS SELECT * FROM read_parquet('data/concept.parquet');
-- ... repeat for all OMOP tables
```

### Create an Ontop Virtual Repository in GraphDB

1. Open GraphDB Workbench at [http://localhost:7200](http://localhost:7200)
2. Go to **Setup → Repositories → Create new repository**
3. Select **Ontop Virtual Repository**
4. Configure:
   - **Driver class**: `org.duckdb.DuckDBDriver`
   - **JDBC URL**: `jdbc:duckdb:/absolute/path/to/db/OMOP.duckdb`
   - **Mapping**: upload `mappings/OMOP-duckdb.obda`
   - **Ontology**: upload `ontology/OMOP.ttl`

The same SPARQL queries from above will work in the GraphDB SPARQL interface.

---

## Connection to the core tutorial

This use case follows the same three-artifact pattern as the solar system
exercise:

| Artifact | Solar system | OMOP CDM |
|----------|-------------|----------|
| Database | PostgreSQL | DuckDB (Parquet) |
| `.properties` | `solar_system.properties` | `OMOP.properties` |
| `.obda` | `solar_system.obda` | `OMOP-parquet.obda` |
| `.ttl` | `solar_system.ttl` | `OMOP.ttl` |

The only differences are the database backend (DuckDB vs PostgreSQL) and
the domain-specific SQL queries and RDF vocabulary. The Ontop workflow
remains the same.
