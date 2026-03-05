---
title: "Use Case: GBIF Biodiversity Data"
---

# Use Case: GBIF Biodiversity Data

The [Global Biodiversity Information Facility (GBIF)](https://www.gbif.org/)
publishes monthly snapshots of all occurrence records as Parquet files on
Amazon S3. Using the same Ontop + DuckDB approach from the core tutorial,
you can expose these biodiversity records as a SPARQL endpoint — another
example of the VKG pattern applied to a different domain.

The full GBIF dataset contains billions of records spread across ~2800
Parquet shards. Querying it live on AWS is not practical with Ontop because
every SPARQL query would trigger a full scan of all shards. Instead, we
extract a country-level subset first, then map it with Ontop.

This chapter uses **Montserrat** (country code `MS`, ~50k records, ~5 MB)
as a quick example, and **Suriname** (`SR`, ~500k records, ~65 MB) as a
more realistic case.

---

## Prerequisites

- DuckDB installed (see [Installation](installation.md))
- Ontop CLI installed and on your PATH
- Internet access (to download from AWS S3)

---

## Step 1 — Extract a country subset from GBIF

GBIF publishes monthly snapshots at:

```
s3://gbif-open-data-us-east-1/occurrence/YYYY-MM-01/occurrence.parquet/
```

The `extract_country.sh` script automates the extraction. It:

1. Lists all Parquet shards in the S3 bucket for a given month
2. Generates a DuckDB SQL query that scans all shards and filters by country code
3. Runs the query to produce a single local Parquet file

### The extraction script

Save this as `extract_country.sh`:

```bash
#!/bin/bash

# === Input Parameters ===
YEAR=$1
MONTH=$2
COUNTRYCODE=$3

if [ -z "$YEAR" ] || [ -z "$MONTH" ] || [ -z "$COUNTRYCODE" ]; then
  echo "Usage: ./extract_country.sh <year> <month> <country_code>"
  echo "Example: ./extract_country.sh 2025 02 SR"
  exit 1
fi

# === Zero-pad month ===
MONTH=$(printf "%02d" $MONTH)
echo "[$(date "+%Y-%m-%d %H:%M:%S")] Step 1: Listing files in S3 bucket..."

# === Step 1: List files in S3 bucket ===
S3_PATH="s3://gbif-open-data-us-east-1/occurrence/${YEAR}-${MONTH}-01/occurrence.parquet/"
FILES=$(aws s3 ls "$S3_PATH" --no-sign-request | awk '{print $4}')

if [ -z "$FILES" ]; then
  echo "!! No files found for $YEAR-$MONTH!"
  exit 1
fi
echo "[$(date "+%Y-%m-%d %H:%M:%S")]  Found files in S3."

# === Step 2: Build DuckDB SQL ===
echo "[$(date "+%Y-%m-%d %H:%M:%S")]  Step 2: Building DuckDB SQL query..."
SAFE_COUNTRYCODE=$(echo "$COUNTRYCODE" | tr ',' '_')
SQL_FILE="query_${SAFE_COUNTRYCODE}_${YEAR}_${MONTH}.sql"
PARQUET_FILE="occurrence_${SAFE_COUNTRYCODE}_${YEAR}_${MONTH}.parquet"

echo "INSTALL httpfs;" > $SQL_FILE
echo "LOAD httpfs;" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "COPY (" >> $SQL_FILE
echo "  SELECT *" >> $SQL_FILE
echo "  FROM parquet_scan([" >> $SQL_FILE

for FILE in $FILES; do
  echo "    'https://gbif-open-data-us-east-1.s3.amazonaws.com/occurrence/${YEAR}-${MONTH}-01/occurrence.parquet/$FILE'," >> $SQL_FILE
done

# Remove trailing comma
sed -i '' '$ s/,$//' $SQL_FILE

echo "  ])" >> $SQL_FILE

# === Build WHERE clause ===
if [[ "$COUNTRYCODE" == *","* ]]; then
  COUNTRY_LIST=$(echo "$COUNTRYCODE" | awk -v q="'" -F',' \
    '{for (i=1; i<=NF; i++) printf q tolower($i) q (i<NF?",":"")}')
  echo "  WHERE lower(countrycode) IN (${COUNTRY_LIST})" >> $SQL_FILE
else
  echo "  WHERE lower(countrycode) = lower('${COUNTRYCODE}')" >> $SQL_FILE
fi
echo ") TO '${PARQUET_FILE}' (FORMAT PARQUET);" >> $SQL_FILE

echo "[$(date "+%Y-%m-%d %H:%M:%S")]  SQL saved to: $SQL_FILE"

# === Step 3: Run the query ===
echo "[$(date "+%Y-%m-%d %H:%M:%S")]  Step 3: Running DuckDB query..."
duckdb < $SQL_FILE
echo "[$(date "+%Y-%m-%d %H:%M:%S")] Done! File saved: $PARQUET_FILE"
```

:::{note}
This script requires the [AWS CLI](https://aws.amazon.com/cli/) to list
the S3 bucket contents. No AWS account or credentials are needed —
GBIF's bucket is public (`--no-sign-request`).
:::

### Run the extraction

```bash
chmod +x extract_country.sh

# Montserrat (small, fast — good for testing)
./extract_country.sh 2025 02 MS

# Suriname (larger, more realistic)
./extract_country.sh 2025 02 SR
```

You can also extract multiple countries at once:

```bash
./extract_country.sh 2025 02 SR,GY,GF
```

:::{warning}
Extracting data scans all ~2800 Parquet shards on S3. This requires a good
internet connection and may take several minutes depending on your bandwidth.
:::

---

## Step 2 — Create the OBDA mapping

GBIF occurrence records use [Darwin Core](https://dwc.tdwg.org/terms/)
terminology. The mapping file translates DuckDB columns into Darwin Core
RDF properties.

Save this as `gbif-mapping.obda`:

```
[PrefixDeclaration]
ex:  http://example.org/occurrence/
dwc: http://rs.tdwg.org/dwc/terms/
geo: http://www.opengis.net/ont/geosparql#
wdt: http://www.wikidata.org/prop/direct/

[MappingDeclaration] @collection [[
mappingId   occurrence_all_fields
target      <http://example.org/occurrence/{gbifid}> a dwc:Occurrence ;
              ex:gbifID "{gbifid}" ;
              dwc:datasetKey "{datasetkey}" ;
              dwc:occurrenceID "{occurrenceid}" ;
              dwc:kingdom "{kingdom}" ;
              dwc:phylum "{phylum}" ;
              dwc:class "{class}" ;
              dwc:order "{order}" ;
              dwc:family "{family}" ;
              dwc:genus "{genus}" ;
              dwc:species "{species}" ;
              dwc:infraspecificEpithet "{infraspecificepithet}" ;
              dwc:taxonRank "{taxonrank}" ;
              dwc:scientificName "{scientificname}" ;
              dwc:verbatimScientificName "{verbatimscientificname}" ;
              dwc:verbatimScientificNameAuthorship "{verbatimscientificnameauthorship}" ;
              dwc:countryCode "{countrycode}" ;
              dwc:locality "{locality}" ;
              dwc:stateProvince "{stateprovince}" ;
              dwc:occurrenceStatus "{occurrencestatus}" ;
              dwc:individualCount "{individualcount}" ;
              dwc:publishingOrgKey "{publishingorgkey}" ;
              dwc:decimalLatitude "{decimallatitude}" ;
              dwc:decimalLongitude "{decimallongitude}" ;
              dwc:coordinateUncertaintyInMeters "{coordinateuncertaintyinmeters}" ;
              dwc:coordinatePrecision "{coordinateprecision}" ;
              dwc:elevation "{elevation}" ;
              dwc:elevationAccuracy "{elevationaccuracy}" ;
              dwc:depth "{depth}" ;
              dwc:depthAccuracy "{depthaccuracy}" ;
              dwc:eventDate "{eventdate}" ;
              dwc:day "{day}" ;
              dwc:month "{month}" ;
              dwc:year "{year}" ;
              dwc:taxonKey "{taxonkey}" ;
              dwc:speciesKey "{specieskey}" ;
              dwc:basisOfRecord "{basisofrecord}" ;
              dwc:institutionCode "{institutioncode}" ;
              dwc:collectionCode "{collectioncode}" ;
              dwc:catalogNumber "{catalognumber}" ;
              dwc:recordNumber "{recordnumber}" ;
              dwc:identifiedBy "{identifiedby}" ;
              dwc:dateIdentified "{dateidentified}" ;
              dwc:license "{license}" ;
              dwc:rightsHolder "{rightsholder}" ;
              dwc:recordedBy "{recordedby}" ;
              dwc:typeStatus "{typestatus}" ;
              dwc:establishmentMeans "{establishmentmeans}" ;
              dwc:lastInterpreted "{lastinterpreted}" ;
              dwc:mediaType "{mediatype}" ;
              dwc:issue "{issue}" ;
              wdt:P625 "Point({decimallongitude} {decimallatitude})"^^geo:wktLiteral .
source      SELECT gbifid, datasetkey, occurrenceid, kingdom, phylum, class,
              "order", family, genus, species, infraspecificepithet, taxonrank,
              scientificname, verbatimscientificname,
              verbatimscientificnameauthorship, countrycode, locality,
              stateprovince, occurrencestatus, individualcount, publishingorgkey,
              decimallatitude, decimallongitude, coordinateuncertaintyinmeters,
              coordinateprecision, elevation, elevationaccuracy, depth,
              depthaccuracy, eventdate, day, month, year, taxonkey, specieskey,
              basisofrecord, institutioncode, collectioncode, catalognumber,
              recordnumber, identifiedby, dateidentified, license, rightsholder,
              recordedby, typestatus, establishmentmeans, lastinterpreted,
              mediatype, issue
            FROM 'occurrence_MS_2025_02.parquet'
]]
```

:::{tip}
Change the `FROM` clause filename to match your extracted Parquet file
(e.g. `occurrence_SR_2025_02.parquet` for Suriname).
:::

---

## Step 3 — Create a minimal ontology

Save this as `gbif.ttl`:

```turtle
@prefix dwc: <http://rs.tdwg.org/dwc/terms/> .
@prefix ex:  <http://example.org/occurrence/> .
```

---

## Step 4 — Create the properties file

Save this as `gbif.properties`:

```properties
jdbc.driver=org.duckdb.DuckDBDriver
jdbc.url=jdbc:duckdb:
```

---

## Step 5 — Start the SPARQL endpoint

```bash
ontop endpoint \
    --ontology gbif.ttl \
    --mapping gbif-mapping.obda \
    --properties gbif.properties \
    --port=8082
```

Open: [http://localhost:8082](http://localhost:8082)

---

## Example SPARQL queries

### Count all occurrences

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT (COUNT(?occ) AS ?count)
WHERE {
  ?occ a dwc:Occurrence .
}
```

### List species with their taxonomic hierarchy

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?species ?genus ?family ?order
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:species ?species ;
       dwc:genus ?genus ;
       dwc:family ?family ;
       dwc:order ?order .
}
LIMIT 20
```

### Count occurrences per institution

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?institution (COUNT(?occ) AS ?count)
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:institutionCode ?institution .
}
GROUP BY ?institution
ORDER BY DESC(?count)
```

### Occurrences with coordinates (GeoSPARQL)

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?species ?coord
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:species ?species ;
       wdt:P625 ?coord .
}
LIMIT 20
```

### Count species per family

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?family (COUNT(DISTINCT ?species) AS ?speciesCount)
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:family ?family ;
       dwc:species ?species .
}
GROUP BY ?family
ORDER BY DESC(?speciesCount)
LIMIT 20
```

---

## Can I query GBIF on AWS directly (without downloading)?

**Not practically with Ontop.** The full GBIF dataset consists of ~2800
Parquet shards totalling hundreds of gigabytes. Ontop translates each SPARQL
query into SQL, and DuckDB would need to scan all shards over the network
for every query. This makes direct S3 querying impractical for interactive
SPARQL use.

The recommended workflow is:

```
GBIF Parquet on S3 → DuckDB extract by country → local Parquet → Ontop → SPARQL
```

You **can** query GBIF's S3 Parquet files directly with DuckDB for one-off
analytical queries (using `httpfs`), but Ontop's virtual mapping approach
works best with local data where repeated SQL access is fast.

:::{tip}
For the fastest experience, a local Parquet file will always outperform a
remote S3 copy. Even the full Suriname extract (~65 MB) responds to SPARQL
queries in milliseconds via Ontop.
:::

---

## Connection to the core tutorial

Like the OMOP use case, GBIF follows the same three-artifact VKG pattern:

| Artifact | Solar system | GBIF |
|----------|-------------|------|
| Database | PostgreSQL | DuckDB (Parquet) |
| `.properties` | `solar_system.properties` | `gbif.properties` |
| `.obda` | `solar_system.obda` | `gbif-mapping.obda` |
| `.ttl` | `solar_system.ttl` | `gbif.ttl` |

The GBIF mapping uses [Darwin Core](https://dwc.tdwg.org/terms/) vocabulary
instead of a custom ontology, demonstrating how Ontop can map to established
community standards.
