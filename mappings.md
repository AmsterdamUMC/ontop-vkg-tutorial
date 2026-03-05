---
title: "OBDA Mappings"
authors:
  - name: "Carsten Fortmann-Grote"
    orcid: "https://orcid.org/0000-0002-2579-5546"
  - name: "Rowdy de Groot"
    orcid: "https://orcid.org/0000-0002-1248-1986"
  - name: "Andra Waagmeester"
    orcid: "https://orcid.org/0000-0001-9773-4008"
---

# OBDA Mappings

The heart of Ontop4OMOP is a set of **OBDA (Ontology-Based Data Access)
mapping rules** written in the `.obda` format. These rules declaratively
define how SQL query results are translated into RDF triples — without
ever materializing an RDF file on disk.

---

## How OBDA mappings work

Each mapping rule has three parts:

| Part | Purpose |
|------|---------|
| `mappingId` | A unique name for the rule |
| `source` | A SQL SELECT query that retrieves data |
| `target` | An RDF triple pattern using variables from the SQL result |

At query time, Ontop rewrites an incoming SPARQL query into SQL, executes it
against the database, and returns the results as RDF — all on the fly.

---

## Namespace prefixes

The mapping file declares the following prefixes:

```
ex:    http://example.org/omop/
omop:  http://www.ohdsi.org/omop#
rdf:   http://www.w3.org/1999/02/22-rdf-syntax-ns#
rdfs:  http://www.w3.org/2000/01/rdf-schema#
owl:   http://www.w3.org/2002/07/owl#
xsd:   http://www.w3.org/2001/XMLSchema#
```

- `ex:` — base IRI for all OMOP instance identifiers (e.g. `ex:person/1`)
- `omop:` — OMOP CDM ontology terms (classes and properties)

---

## Mapping rules by OMOP domain

### Person

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

Each `person_id` in the Parquet file becomes an IRI of the form
`http://example.org/omop/person/1`, typed as `omop:Person`.

---

### Visit Occurrence

```
mappingId      visit_class
target         ex:visit/{visit_occurrence_id} a omop:VisitOccurrence .
source         SELECT visit_occurrence_id FROM read_parquet('visit_occurrence.parquet')

mappingId      visit_person
target         ex:visit/{visit_occurrence_id} omop:person ex:person/{person_id} .
source         SELECT visit_occurrence_id, person_id FROM read_parquet('visit_occurrence.parquet')

mappingId      visit_type
target         ex:visit/{visit_occurrence_id} omop:visitConcept ex:concept/{visit_concept_id} .
source         SELECT visit_occurrence_id, visit_concept_id FROM read_parquet('visit_occurrence.parquet')
```

---

### Condition Occurrence

```
mappingId      condition_class
target         ex:condition/{condition_occurrence_id} a omop:ConditionOccurrence .
source         SELECT condition_occurrence_id FROM read_parquet('condition_occurrence.parquet')

mappingId      condition_person
target         ex:condition/{condition_occurrence_id} omop:person ex:person/{person_id} .
source         SELECT condition_occurrence_id, person_id FROM read_parquet('condition_occurrence.parquet')

mappingId      condition_concept
target         ex:condition/{condition_occurrence_id} omop:conditionConcept ex:concept/{condition_concept_id} .
source         SELECT condition_occurrence_id, condition_concept_id FROM read_parquet('condition_occurrence.parquet')
```

---

### Drug Exposure

```
mappingId      drug_class
target         ex:drug/{drug_exposure_id} a omop:DrugExposure .
source         SELECT drug_exposure_id FROM read_parquet('drug_exposure.parquet')

mappingId      drug_person
target         ex:drug/{drug_exposure_id} omop:person ex:person/{person_id} .
source         SELECT drug_exposure_id, person_id FROM read_parquet('drug_exposure.parquet')

mappingId      drug_concept
target         ex:drug/{drug_exposure_id} omop:drugConcept ex:concept/{drug_concept_id} .
source         SELECT drug_exposure_id, drug_concept_id FROM read_parquet('drug_exposure.parquet')
```

---

### Measurement

```
mappingId      measurement_class
target         ex:measurement/{measurement_id} a omop:Measurement .
source         SELECT measurement_id FROM read_parquet('measurement.parquet')

mappingId      measurement_person
target         ex:measurement/{measurement_id} omop:person ex:person/{person_id} .
source         SELECT measurement_id, person_id FROM read_parquet('measurement.parquet')

mappingId      measurement_concept
target         ex:measurement/{measurement_id} omop:measurementConcept ex:concept/{measurement_concept_id} .
source         SELECT measurement_id, measurement_concept_id FROM read_parquet('measurement.parquet')
```

---

## Two mapping files

The repository ships with two mapping files for different modes:

| File | Mode | SQL source |
|------|------|------------|
| `mappings/OMOP-parquet.obda` | CLI mode | `read_parquet('file.parquet')` |
| `mappings/OMOP-duckdb.obda` | GraphDB Desktop mode | `SELECT ... FROM <table>` (DuckDB views) |

The CLI mode reads Parquet files directly; the GraphDB mode queries persistent
tables in a DuckDB `.duckdb` file.

---

## Key rules for writing OBDA mappings

:::{important}
When authoring or extending mapping rules, observe these constraints:

- **No semicolons** at the end of SQL source queries
- **No default `:` prefix** — always use an explicit prefix like `ex:`
- SQL identifiers must match the column names in the Parquet/database schema
:::
