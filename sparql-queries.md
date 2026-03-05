---
title: "SPARQL Queries"
---

# SPARQL Queries

The following queries can be run against the SPARQL endpoint started in
[CLI mode](cli-endpoint.md) (`http://localhost:8081/sparql`) or via
[GraphDB Desktop](graphdb-mode.md) (`http://localhost:7200/sparql`).

---

## Namespace prefixes

All queries use these prefixes:

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

---

## Query 1 — Count all persons

A basic connectivity test. If this returns a positive number, the endpoint
is working correctly.

```sparql
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT (COUNT(?p) AS ?count)
WHERE {
  ?p a omop:Person .
}
```

---

## Query 2 — List persons with gender and birth year

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?person ?genderConcept ?birthYear
WHERE {
  ?person a omop:Person .
  OPTIONAL { ?person omop:hasGenderConcept ?genderConcept . }
  OPTIONAL { ?person omop:yearOfBirth ?birthYear . }
}
LIMIT 20
```

---

## Query 3 — List visits per person

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?person ?visit
WHERE {
  ?visit a omop:VisitOccurrence .
  ?visit omop:person ?person .
}
LIMIT 20
```

---

## Query 4 — List visits with visit type concept

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?person ?visit ?visitConcept
WHERE {
  ?visit a omop:VisitOccurrence .
  ?visit omop:person ?person .
  OPTIONAL { ?visit omop:visitConcept ?visitConcept . }
}
LIMIT 20
```

---

## Query 5 — List conditions with concept

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?condition ?concept
WHERE {
  ?condition a omop:ConditionOccurrence .
  ?condition omop:conditionConcept ?concept .
}
LIMIT 20
```

---

## Query 6 — Count conditions per person

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

---

## Query 7 — Drug exposures for a specific person

Replace `ex:person/1` with the IRI of the person you want to inspect.

```sparql
PREFIX ex:   <http://example.org/omop/>
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?drug ?drugConcept
WHERE {
  ?drug a omop:DrugExposure .
  ?drug omop:person ex:person/1 .
  OPTIONAL { ?drug omop:drugConcept ?drugConcept . }
}
```

---

## Query 8 — Measurements per person

```sparql
PREFIX omop: <http://www.ohdsi.org/omop#>

SELECT ?person ?measurement ?measurementConcept
WHERE {
  ?measurement a omop:Measurement .
  ?measurement omop:person ?person .
  OPTIONAL { ?measurement omop:measurementConcept ?measurementConcept . }
}
LIMIT 20
```

---

## Query 9 — All clinical facts for one person

A federated overview of all clinical data for a single patient:

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

## Tips

:::{tip}
- Use `LIMIT` to avoid large result sets during exploration
- The Ontop SPARQL workbench at `http://localhost:8081` has auto-completion
- SPARQL property paths (`omop:person/omop:hasGenderConcept`) can traverse multiple hops
:::
