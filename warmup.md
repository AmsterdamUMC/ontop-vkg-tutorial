---
title: "Warmup: Tabular Data to RDF"
---

# Warmup: Converting Tabular Data to RDF

Before diving into the Ontop framework, this chapter introduces the
fundamental relationship between tabular data and RDF triples using a
hands-on Python exercise.

## Learning objectives

- Convert a table of planetary physical properties to RDF
- Query the generated RDF file with `arq` (from Apache Jena)
- Understand the relationship between long and wide tabular data and RDF triples

---

## The planets dataset

We work with a small dataset listing geophysical properties of the
8 planets in our solar system (originally extracted from Wikidata):

| id   | planetLabel | distance_to_sun | rotation_period | orbital_period | density | mass      | temperature |
|------|-------------|-----------------|-----------------|----------------|---------|-----------|-------------|
| Q308 | Mercury     | 69817445934     | 5097600         | 7600522        | 5427    | 330       | 700         |
| Q313 | Venus       | 108942109000    | 20997000        | 19414148       | 5243    | 4868      | 747         |
| Q2   | Earth       | 152098231559    | 86400           | 31558150       | 5513    | 5972      | 288         |
| Q111 | Mars        | 249232432000    | 88642           | 59355072       | 3933    | 642       | 308         |
| Q319 | Jupiter     | 816520700000    | 35640           | 374335690      | 1326    | 1898130   |             |
| Q193 | Saturn      | 1514500000000   | 38520           | 929468434      | 867     | 568360    | 134         |
| Q324 | Uranus      | 3006318143000   | 61200           | 2651486400     | 1271    | 86810     | 57          |
| Q332 | Neptune     | 4537039826000   | 57600           | 5200692480     | 1638    | 102430    | 72          |

The data file `planets.csv` is available in the tutorial repository.

---

## Wide and long tables

This table is in **wide format**: one record per row, with all property
values as columns. Our goal is to convert it to a set of RDF triples
`(subject, predicate, object)`.

An RDF triple for planet Earth might look like this in Turtle syntax:

```turtle
:Q2 :name "Earth"@en .
```

The conversion logic for a wide table is straightforward:

1. For each row (record) in the table:
   - The **record's ID** becomes the triple's **subject**
   - For each column value in that row:
     - The **column header** becomes the **predicate**
     - The **cell value** becomes the **object**

### Converting to long format

A useful intermediate step is to first convert ("melt" or "unpivot") the
wide table to a **long table** with three columns: `id`, `property_name`,
and `property_value`:

```python
import pandas

# Read data in wide format
wide_table = pandas.read_csv('planets.csv', sep=",", header=0)

# Melt to long format
long_table = wide_table.melt(
    id_vars="id",
    value_vars=wide_table.columns[1:],
    var_name="property_name",
    value_name="property_value"
).sort_values(["id", "property_name"])
```

The resulting long table has exactly three columns — each row is
already a triple `(id, property_name, property_value)`:

```
      id    property_name   property_value
35  Q111          density           3933.0
11  Q111  distance_to_sun   249232432000.0
43  Q111             mass            642.0
3   Q111      planetLabel             Mars
27  Q111   orbital_period       59355072.0
19  Q111  rotation_period          88642.0
51  Q111      temperature            308.0
```

---

## Making it proper RDF

To turn the long table into a valid RDF graph, we need IRIs (Internationalized
Resource Identifiers) instead of plain strings. We define a namespace prefix:

```turtle
@prefix : <http://example.org/planets#> .
```

And some standard W3C prefixes:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

We also add some semantics:
- Declare a class `:Planet` — `(:Planet a owl:Class)`
- Declare each column header as an RDF property — `(:name a rdf:Property)`
- State that each record is an instance of `:Planet` — `(:Q2 a :Planet)`

---

## Python implementation

Here is the complete conversion script (`pandas2rdf.py`):

```python
import pandas
from rdflib import Graph, Literal
import rdflib.namespace as nslib
from rdflib.namespace import RDF, OWL

# Create RDF graph
graph = Graph(bind_namespaces='core')

# Define namespace
planets_ns = "http://example.org/planets#"
planets = nslib.Namespace(planets_ns)
graph.bind("planets", planets_ns)
graph.bind("", planets_ns)

# Add class declaration
graph.add((planets.Planet, RDF.type, OWL['Class']))

# Load CSV and convert to long table
wide_table = pandas.read_csv('planets.csv', sep=",", header=0)
long_table = wide_table.melt(
    id_vars="id",
    value_vars=wide_table.columns[1:],
    var_name="property_name",
    value_name="property_value"
).sort_values(["id", "property_name"])

# Add property declarations
for column in wide_table.columns[1:]:
    graph.add((planets[column], RDF.type, RDF.Property))

# Convert each row to a triple
for record in long_table.to_dict(orient='records'):
    id, prop, val = record.values()
    graph.add((planets[id], RDF.type, planets.Planet))
    graph.add((planets[id], planets[prop], Literal(val)))

# Serialize to Turtle
graph.serialize("planets.ttl")
```

Run the script:

```bash
python pandas2rdf.py
```

The output `planets.ttl` will contain triples like:

```turtle
@prefix : <http://example.org/planets#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:Q111 a :Planet ;
    :density 3.933e+03 ;
    :distance_to_sun 2.492324e+11 ;
    :mass 6.42e+02 ;
    :planetLabel "Mars" .

:Planet a owl:Class .
:density a rdf:Property .
:distance_to_sun a rdf:Property .
```

---

## Querying with SPARQL

We can verify the generated RDF using `arq` from
[Apache Jena](https://jena.apache.org/download/):

```bash
echo 'prefix : <http://example.org/planets#>
      select * where {
             ?planet a :Planet;
                     :planetLabel ?name .
      }
' > query.rq

arq --data=planets.ttl --query query.rq
```

Expected output:

```
----------------------
| planet | name      |
======================
| :Q193  | "Saturn"  |
| :Q332  | "Neptune" |
| :Q308  | "Mercury" |
| :Q313  | "Venus"   |
| :Q324  | "Uranus"  |
| :Q111  | "Mars"    |
| :Q319  | "Jupiter" |
| :Q2    | "Earth"   |
----------------------
```

---

## Discussion

- In which aspects is this example overly simplistic?
- What would you do differently?

---

## Assignment: Moons dataset

The file `moons.csv` contains data about the moons (natural satellites) in
our solar system.

Convert it to a Turtle-formatted RDF file.

:::{hint}
How do you treat the data in the `mother_planet_id` column? Unlike other
values (which are literals), this column refers to an entity in the planets
table — so it should become an IRI reference, not a string literal.
:::

:::{admonition} Solution
:class: dropdown

```python
import pandas
from rdflib import Graph, Literal
import rdflib.namespace as nslib
from rdflib.namespace import RDF, OWL

graph = Graph(bind_namespaces='core')

planets_ns = "http://example.org/planets#"
planets = nslib.Namespace(planets_ns)
graph.bind("planets", planets_ns)
graph.bind("", planets_ns)
graph.add((planets.Moon, RDF.type, OWL['Class']))

wide_table = pandas.read_csv('moons.csv', sep=",", header=0)
long_table = wide_table.melt(
    id_vars="id",
    value_vars=wide_table.columns[1:],
    var_name="property_name",
    value_name="property_value"
).sort_values(["id", "property_name"])

for column in wide_table.columns[1:]:
    graph.add((planets[column], RDF.type, RDF.Property))

for record in long_table.to_dict(orient='records'):
    id, prop, val = record.values()
    graph.add((planets[id], RDF.type, planets.Moon))
    if str(val) == 'nan':
        continue
    if prop == 'mother_planet_id':
        # Foreign key → IRI reference, not a literal
        graph.add((planets[id], planets[prop], planets[val]))
    else:
        graph.add((planets[id], planets[prop], Literal(val)))

graph.serialize('moons.ttl')
```
:::
