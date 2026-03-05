---
title: "OBDA Mappings with Ontop"
---

# Converting Relational Databases to RDF with Ontop

In the warmup we converted a CSV file to RDF using Python. In practice,
data lives in relational databases with multiple related tables. The
**Ontop** framework provides a way to expose such databases as RDF through
**OBDA (Ontology-Based Data Access)** mappings — without materializing
any triples.

## Learning objectives

- Understand the basics of the OBDA mapping language
- Launch an Ontop SPARQL endpoint over a PostgreSQL database
- Write and extend mappings for a solar system database

---

## From tables to triples

In the warmup, we saw how to map a wide table to RDF. Relational databases
are not much different: a database consists of one or more wide tables. Each
table has a **primary key** column indexing its records. Relations between
records are established through **foreign key** columns.

Consider our two tables `planets` and `moons`:

- In both tables, the `id` column is the **primary key**
- In `moons`, the `mother_planet_id` column is a **foreign key** pointing
  to `planets.id`

---

## The OBDA mapping language

An Ontop mapping is a pair of **source** (SQL query) and **target**
(RDF template). The source query retrieves tabular data; the target
template specifies how each row becomes RDF triples.

### Example

Suppose we want to generate these triples from the `planets` table:

```turtle
:Q2   :name "Earth" .
:Q313 :name "Venus" .
```

The **source** SQL query:

```sql
SELECT id, name FROM planets;
```

Returns:

| id   | name    |
|------|---------|
| Q308 | Mercury |
| Q313 | Venus   |
| Q2   | Earth   |
| ...  | ...     |

The **target** template:

```turtle
:{id} :name "{name}"^^xsd:string .
```

Tokens in curly braces `{...}` are **template arguments** — they are replaced
by values from the corresponding SQL column for each row. This generates as
many triples as there are rows in the query result.

### The OBDA file format

Mappings are stored in `.obda` files with this structure:

```
[PrefixDeclaration]
:        http://example.org/planets#
owl:     http://www.w3.org/2002/07/owl#
rdf:     http://www.w3.org/1999/02/22-rdf-syntax-ns#
xsd:     http://www.w3.org/2001/XMLSchema#

[MappingDeclaration] @collection [[
mappingId   planet_dataproperties
target      :Planet/{id} a :Planet ; :name {name}^^xsd:string .
source      SELECT id, name FROM planets
]]
```

Each mapping has:
- A **mappingId** — a unique identifier
- A **target** — Turtle-syntax template with `{column}` placeholders
- A **source** — a SQL `SELECT` query

---

## Combining multiple tables

SQL supports JOINs to combine data from multiple tables. For example, to
add the mother planet's mass to each moon:

```sql
SELECT moons.id    AS moon_id,
       moons.name  AS moon_name,
       planets.name AS mother_planet,
       planets.mass AS mother_planet_mass
FROM moons
JOIN planets ON moons.mother_planet_id = planets.id
LIMIT 10;
```

| moon_id | moon_name  | mother_planet | mother_planet_mass |
|---------|------------|---------------|--------------------|
| Q17762  | Aegaeon    | Saturn        | 568360             |
| Q17788  | Anthe      | Saturn        | 568360             |
| Q3303   | Enceladus  | Saturn        | 568360             |
| Q3134   | Callisto   | Jupiter       | 1898130            |
| ...     | ...        | ...           | ...                |

The source query in an OBDA mapping can be any valid SQL — including JOINs,
aggregations, subqueries, and CTEs.

---

## Ontologies

Each Ontop mapping is accompanied by an OWL **ontology** file (`.ttl`). In the
warmup, we added class and property declarations directly to the RDF output.
With Ontop, these declarations go into a separate ontology file.

The ontology enables **inference**. For example, instead of explicitly stating
`:Q2 a :Planet`, we can declare:

```turtle
:distance_to_sun a rdf:Property ;
                 rdfs:domain :Planet .
```

Now every subject with a `:distance_to_sun` property is automatically inferred
to be a `:Planet`. The ontology also allows importing third-party vocabularies
for richer semantics and can improve query performance.

---

## Hands-on: Solar system VKG

### Prerequisites

For this exercise you need:
- Ontop CLI installed (see [Installation](installation.md))
- Access to the tutorial PostgreSQL database, or a local PostgreSQL
  instance with the solar system data loaded

:::{note}
The SWAT4HCLS tutorial provides a shared PostgreSQL instance. If you are
working through this tutorial independently, you can create your own
database by importing `planets.csv` and `moons.csv` (see the
[data preparation appendix](#loading-csv-into-postgresql)).
:::

### Step 1 — Create the configuration files

Create a directory for your VKG project:

```bash
mkdir solar_system_vkg
cd solar_system_vkg
```

#### Properties file (`solar_system.properties`)

This file tells Ontop how to connect to the database:

```properties
jdbc.password=solar
jdbc.user=solar_system
jdbc.url=jdbc\:postgresql\://localhost\:5432/solar_system
jdbc.driver=org.postgresql.Driver
```

:::{tip}
Update the `jdbc.url` to match your PostgreSQL host and port.
:::

#### Ontology file (`solar_system.ttl`)

A minimal ontology declaring the `Planet` class and the `name` property:

```turtle
@prefix : <http://example.org/planets#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix planets: <http://example.org/planets#> .
@base <http://example.org/planets#> .

<http://example.org/ontologies/solar_system> rdf:type owl:Ontology ;
    dcterms:license "https://creativecommons.org/publicdomain/zero/1.0/" ;
    rdfs:label "Solar System Ontology" ;
    skos:definition "Ontology for the Solar System" .

planets:name rdf:type owl:DatatypeProperty .
planets:Planet rdf:type owl:Class .
```

#### Mapping file (`solar_system.obda`)

Start with a minimal mapping for planet names:

```
[PrefixDeclaration]
:        http://example.org/planets#
planets: http://example.org/planets#
owl:     http://www.w3.org/2002/07/owl#
rdf:     http://www.w3.org/1999/02/22-rdf-syntax-ns#
xsd:     http://www.w3.org/2001/XMLSchema#
rdfs:    http://www.w3.org/2000/01/rdf-schema#
obda:    https://w3id.org/obda/vocabulary#
skos:    http://www.w3.org/2004/02/skos/core#
dcterms: http://purl.org/dc/terms/

[MappingDeclaration] @collection [[
mappingId   planet_dataproperties
target      :Planet/{id} a :Planet ; :name {name}^^xsd:string .
source      SELECT id, name FROM planets
]]
```

### Step 2 — Launch the Ontop endpoint

```bash
ontop endpoint \
    --properties solar_system.properties \
    --mapping solar_system.obda \
    --ontology solar_system.ttl \
    --cors-allowed-origins=* \
    --dev
```

You should see output ending with:

```
-INFO  in i.u.i.o.e.OntopEndpointApplication - Started OntopEndpointApplication
```

Open [http://localhost:8080](http://localhost:8080) to access the Ontop
SPARQL UI.

### Step 3 — Test with a simple query

In the Ontop UI, run:

```sparql
SELECT * WHERE {
  ?sub ?pred ?obj
}
LIMIT 20
```

You should see results like:

| sub | pred | obj |
|-----|------|-----|
| `planets:Planet/Q308` | `rdf:type` | `planets:Planet` |
| `planets:Planet/Q313` | `rdf:type` | `planets:Planet` |
| `planets:Planet/Q308` | `planets:name` | Mercury |
| `planets:Planet/Q313` | `planets:name` | Venus |
| ... | ... | ... |

---

## Assignments

Now extend the mapping to expose more of the solar system data.

### Assignment 1: Planetary properties

The `planets` table has these columns:

- `temperature`, `density`, `mass`, `distance_to_sun`
- `rotation_period`, `orbital_period`, `name`, `id`

Add mappings for the remaining physical properties. You will also need to
add corresponding property declarations to the ontology.

:::{admonition} Hint
:class: dropdown
Add a new mapping (or extend the existing target) with additional property
bindings, for example:

```
target  :Planet/{id} a :Planet ;
            :name {name}^^xsd:string ;
            :mass {mass}^^xsd:decimal ;
            :density {density}^^xsd:decimal ;
            :distance_to_sun {distance_to_sun}^^xsd:decimal ;
            :rotation_period {rotation_period}^^xsd:decimal ;
            :orbital_period {orbital_period}^^xsd:decimal ;
            :temperature {temperature}^^xsd:decimal .
source  SELECT id, name, mass, density, distance_to_sun,
               rotation_period, orbital_period, temperature
        FROM planets
```
:::

### Assignment 2: Moons

Add mappings and ontology terms for the moons table:

- Class `Moon`
- Data properties for moon attributes
- Object property `:hasPlanet` with `rdfs:domain :Moon` and `rdfs:range :Planet`
- Inverse property `:hasMoon` (from Planet to Moon)

### Assignment 3: Test queries

Use the Ontop SPARQL UI to verify your mappings:

```sparql
PREFIX : <http://example.org/planets#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Count planets (should return 8)
ASK WHERE {
  {
    SELECT (COUNT(?planet) AS ?nplanets) WHERE {
      ?planet a :Planet .
    }
  }
  FILTER(?nplanets = "8"^^xsd:integer)
}
```

```sparql
PREFIX : <http://example.org/planets#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Count moons (should return 49)
ASK WHERE {
  {
    SELECT (COUNT(?moon) AS ?nmoons) WHERE {
      ?moon a :Moon .
    }
  }
  FILTER(?nmoons = "49"^^xsd:integer)
}
```

---

## Loading CSV into PostgreSQL

If you don't have access to the shared tutorial database, you can create
your own from the CSV files:

```sql
CREATE DATABASE solar_system;

-- Connect to the database, then:

CREATE TABLE planets (
    id TEXT PRIMARY KEY,
    name TEXT,
    distance_to_sun DOUBLE PRECISION,
    rotation_period DOUBLE PRECISION,
    orbital_period DOUBLE PRECISION,
    density DOUBLE PRECISION,
    mass DOUBLE PRECISION,
    temperature DOUBLE PRECISION
);

CREATE TABLE moons (
    id TEXT PRIMARY KEY,
    name TEXT,
    mother_planet_id TEXT REFERENCES planets(id),
    apoapsis DOUBLE PRECISION,
    density DOUBLE PRECISION,
    radius DOUBLE PRECISION,
    orbital_period DOUBLE PRECISION,
    mass DOUBLE PRECISION,
    temperature DOUBLE PRECISION
);

\COPY planets FROM 'planets.csv' WITH (FORMAT csv, HEADER true);
\COPY moons FROM 'moons.csv' WITH (FORMAT csv, HEADER true);
```
