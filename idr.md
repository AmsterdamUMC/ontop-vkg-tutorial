---
title: "IDR: A Billion-Triple Knowledge Graph"
---

# IDR: A Billion-Triple Knowledge Graph

The [Image Data Resource (IDR)](https://idr.openmicroscopy.org/) is the world's
largest public bioimaging repository, hosting over 14 million microscopy images
across 105 screens and 125 projects from dozens of published studies. Its
metadata is stored in a PostgreSQL database following the OMERO data model — the
same schema introduced in the [OMERO Virtualization](omero.md) chapter.

This chapter applies everything from the tutorial to a real-world, large-scale
deployment: restoring the IDR database, adapting the OBDA mappings, launching a
SPARQL endpoint that returns **resolvable links** to the live IDR web interface,
and materializing over **one billion RDF triples**.

---

## What makes the IDR different

Compared to a typical OMERO installation, the IDR presents several challenges
that require modifications to the standard omero-ontop-mappings:

| Challenge | Typical OMERO | IDR |
|-----------|--------------|-----|
| **Scale** | Thousands of images | 14.3 million images |
| **Annotations** | Thousands of key-value pairs | 86 million key-value pairs |
| **Access control** | Per-group permissions | All data is public |
| **Annotation keys** | Tens of distinct keys | 715 distinct keys |
| **Distinct organisms** | Single lab organism | 84 organisms across studies |

---

## Hardware requirements

The IDR database is large. Plan your infrastructure accordingly.

### Virtual Knowledge Graph endpoint only

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4 vCPUs | 8 vCPUs |
| **RAM** | 8 GB | 32 GB |
| **Disk** | 200 GB SSD | 250 GB SSD |
| **OS** | Ubuntu 24.04 LTS or Debian 12+ | |

The PostgreSQL data directory alone occupies ~167 GB. The additional disk space
is needed for PostgreSQL temp files during complex queries and for the
materialized RDF output.

### Endpoint + materialization

Materialization writes all triples to disk. Budget an extra 5 GB for the
gzipped output and 50 GB of temporary PostgreSQL working space.

### Loading materialized RDF into a triplestore

If you plan to load the materialized file into a dedicated triplestore rather
than using the VKG approach:

| Triplestore | RAM | Disk | Notes |
|-------------|-----|------|-------|
| **QLever** | 32-64 GB | 80-100 GB | Fast; compressed index |
| **GraphDB** | 32-64 GB | 100-150 GB | Includes inference overhead |
| **Jena Fuseki/TDB2** | 16-32 GB | 60-80 GB | Memory-mapped |
| **Blazegraph** | 32-64 GB | 80-120 GB | Journal-based |

---

## Data profile

### IDR entity counts

| Entity | Count |
|--------|------:|
| Annotation key-value pairs | 85,906,467 |
| Channels | 40,300,096 |
| Images | 14,326,844 |
| ROIs | 2,279,539 |
| Wells | 1,980,450 |
| Datasets | 14,909 |
| Plates | 6,762 |
| Projects | 125 |
| Screens | 105 |
| Experimenters | 4 |

### Materialized RDF

| Property | Value |
|----------|-------|
| **Triple count** | 1,030,138,217 |
| File size (gzipped) | 4.9 GB |
| Estimated uncompressed | ~50 GB |
| Format | Turtle (`.ttl.gz`) |
| Serialization time | ~6 hours (8 vCPU, 32 GB RAM) |

---

## Step 1 — Install dependencies

```bash
sudo apt update && sudo apt install -y postgresql openjdk-17-jdk-headless unzip wget
```

Install Ontop CLI (if not already available from earlier chapters):

```bash
cd /opt
sudo wget https://github.com/ontop/ontop/releases/download/ontop-5.3.0/ontop-cli-5.3.0.zip
sudo unzip ontop-cli-5.3.0.zip -d ontop
sudo ln -s /opt/ontop/ontop /usr/local/bin/ontop

# PostgreSQL JDBC driver
sudo wget -O /opt/ontop/jdbc/postgresql-42.7.3.jar \
  https://jdbc.postgresql.org/download/postgresql-42.7.3.jar
```

---

## Step 2 — Restore the PostgreSQL database

The IDR dump is a tar-gzipped PostgreSQL directory-format archive (~11 GB).

### Extract

```bash
tar xzf idr-testing-2024-08-26.tar.gz
# Creates: idr-testing-2024-08-26/ with toc.dat + *.dat.gz files
```

### Create the database

```bash
sudo -u postgres psql -c "CREATE ROLE omero WITH LOGIN PASSWORD 'omero';"
sudo -u postgres psql -c "CREATE ROLE omeroreadonly WITH LOGIN PASSWORD 'omeroreadonly';"
sudo -u postgres createdb -O omero idr
```

### Restore

```bash
sudo -u postgres pg_restore \
  --no-owner \
  --no-privileges \
  --jobs=4 \
  --verbose \
  -d idr \
  /path/to/idr-testing-2024-08-26/
```

This takes approximately 30-45 minutes with 4 parallel jobs on SSD storage.
The restored database is ~167 GB.

### Verify

```bash
sudo -u postgres psql -d idr -c "SELECT count(*) FROM image;"
#  14326844
```

### Create a read-only Ontop user

```bash
sudo -u postgres psql <<'SQL'
CREATE USER ontop WITH PASSWORD 'ontop';
GRANT USAGE ON SCHEMA public TO ontop;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ontop;
SQL
```

---

## Step 3 — Adapt the OBDA mappings for IDR

The mappings are based on the same
[omero-ontop-mappings](https://github.com/German-BioImaging/omero-ontop-mappings)
repository used in the [OMERO chapter](omero.md), but require three
IDR-specific modifications.

### Modification 1: Set the IDR base URL

Change the `ome_instance:` prefix so that all entity IRIs resolve to the live
IDR web interface:

```
ome_instance:   https://idr.openmicroscopy.org/
```

This means a SPARQL result like `https://idr.openmicroscopy.org/Image/1461`
directly links to the IDR viewer for that image.

### Modification 2: Remove access control filters

The upstream mappings include SQL filters for OMERO's group-based permission
model:

```sql
WHERE group_id IN (
  SELECT parent FROM groupexperimentermap WHERE child = ?
)
```

In the IDR, all data is public, but these filters return empty results because
the root user (id 0) belongs only to system groups (0, 1), while all research
data lives in groups 3 and 53. Remove all `group_id` and `owner_id` filters.

### Modification 3: Remove meta-mappings

The upstream repository includes 8 meta-mappings that use Ontop's
`<{map_key}>` syntax to create dynamic RDF predicates from annotation keys:

```
target  ome_instance:Image/{image_id} <{map_key}> {map_value} .
source  SELECT ... FROM annotation_mapvalue
```

With 86 million rows in `annotation_mapvalue`, Ontop's startup
`SELECT DISTINCT` query generates PostgreSQL temp files that exhaust disk space.
These 8 meta-mappings must be removed:

- `MAPID-project-kv-annotations`
- `MAPID-dataset-kv-annotations`
- `MAPID-Image-kv-annotations`
- `MAPID-well-kvannotations`
- `MAPID-plate-kvannotations`
- `MAPID-screen-kvannotations`
- `MAPID-reagent-kvannotations`
- `MAPID-PlateAcquisition-kvannotations`

Annotations remain fully queryable through the structured `MapAnnotation`
mappings that use the `core:mapEntry` / `core:key` / `core:value` pattern:

```sparql
?ann core:mapEntry ?entry .
?entry core:key "Organism" ;
       core:value ?organism .
```

---

## Step 4 — Configuration files

Create a working directory:

```bash
mkdir -p ~/idr-ontop && cd ~/idr-ontop
```

### `idr.properties`

```properties
jdbc.password=ontop
jdbc.user=ontop
jdbc.url=jdbc\:postgresql\://localhost\:5432/idr
jdbc.driver=org.postgresql.Driver
```

### `idr.ttl`

Download the ontology:

```bash
wget -O idr.ttl \
  https://raw.githubusercontent.com/German-BioImaging/omero-ontop-mappings/swat4hcls2026/omero.ttl
```

### `idr.obda`

The complete mapping file with all 51 mappings (IDR-adapted) is available in
the [idrTestOntop repository](https://github.com/AmsterdamUMC/idrTestOntop).
The key mappings are summarised below.

#### Entity identity mappings

Each OMERO entity gets an IRI based on its database `id`, typed with the
corresponding ontology class:

```
mappingId   image-id
target      ome_instance:Image/{id} a core:Image ;
              dc:identifier {id}^^xsd:integer ;
              this:ome_details ome_instance:webclient/img_detail/{id}/ ;
              this:json ome_instance:api/v0/m/images/{id}/ ;
              this:download ome_instance:webgateway/render_image/{id}/ .
source      select id, group_id from image
```

Notice how the image mapping includes three resolvable link properties:

| Property | Resolves to |
|----------|------------|
| `this:ome_details` | IDR web viewer |
| `this:json` | JSON API endpoint |
| `this:download` | Rendered PNG image |

#### Structured annotation mappings

Instead of meta-mappings, annotations are exposed as structured objects:

```
mappingId   MAPID-image-mapannotation-link
target      ome_instance:Image/{image_id} core:hasAnnotation
              ome_instance:MapAnnotation/{ann_id} .
            ome_instance:MapAnnotation/{ann_id} a core:MapAnnotation ;
              dc:identifier {ann_id}^^xsd:integer .
source      select ial.parent as image_id, ial.child as ann_id
            from imageannotationlink ial
            join annotation a on a.id = ial.child
            where a.discriminator = '/map/'

mappingId   MAPID-mapannotation-entries
target      ome_instance:MapAnnotation/{ann_id}
              core:mapEntry ome_instance:MapAnnotation/{ann_id}/entry/{idx} .
            ome_instance:MapAnnotation/{ann_id}/entry/{idx}
              core:key {k}^^xsd:string ;
              core:value {v}^^xsd:string .
source      select annotation_id as ann_id, "index" as idx,
              name as k, value as v
            from annotation_mapvalue
```

---

## Step 5 — Launch the SPARQL endpoint

```bash
cd ~/idr-ontop
ONTOP_JAVA_ARGS='-Xmx8g' ontop endpoint \
  --mapping idr.obda \
  --ontology idr.ttl \
  --properties idr.properties \
  --portal portal.toml \
  --cors-allowed-origins='*' \
  --port=8080
```

:::{note}
The `-Xmx8g` heap is important. The default 512 MB is insufficient for the
IDR's schema size. With 32 GB of system RAM, 8 GB for the JVM leaves plenty
of headroom for PostgreSQL.
:::

Ontop will log warnings about missing `externalinfo` foreign keys — these are
safe to ignore (the corresponding tables are not in the dump). After startup,
the log prints:

```
Ontop has completed the setup and it is ready for query answering!
```

The SPARQL UI is available at `http://<your-ip>:8080` and the protocol endpoint
at `http://<your-ip>:8080/sparql`.

### Running as a systemd service

For production deployments, create `/etc/systemd/system/ontop-idr.service`:

```ini
[Unit]
Description=Ontop IDR SPARQL Endpoint
After=postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/idr-ontop
Environment=ONTOP_JAVA_ARGS=-Xmx8g
ExecStart=/usr/local/bin/ontop endpoint \
  --mapping idr.obda \
  --ontology idr.ttl \
  --properties idr.properties \
  --portal portal.toml \
  --cors-allowed-origins=* \
  --port=8080
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ontop-idr
sudo systemctl start ontop-idr
```

---

## Step 6 — Materialize RDF

To export the entire knowledge graph as a static gzipped Turtle file:

```bash
ONTOP_JAVA_ARGS='-Xmx8g' ontop materialize \
  --mapping idr.obda \
  --ontology idr.ttl \
  --properties idr.properties \
  --output idr-materialized.ttl \
  --format turtle \
  --compression gzip
```

:::{note}
Ontop appends `.ttl.gz` to the output name, producing
`idr-materialized.ttl.ttl.gz`. Rename after completion:
```bash
mv idr-materialized.ttl.ttl.gz idr-materialized.ttl.gz
```
:::

The materialization log will end with:

```
NR of TRIPLES: 1030138217
Elapsed time to materialize: 21142697 {ms}
```

That is **1.03 billion triples** serialized in approximately **6 hours**.

---

## Example SPARQL queries

### List all screens

```sparql
PREFIX omecore: <https://ld.openmicroscopy.org/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?screen ?name
WHERE {
  ?screen a omecore:Screen ;
          rdfs:label ?name .
}
ORDER BY ?name
```

### Images with resolvable viewer links

```sparql
PREFIX omecore: <https://ld.openmicroscopy.org/core/>
PREFIX omekg: <https://ld.openmicroscopy.org/omekg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?image ?name ?viewer ?thumbnail
WHERE {
  ?image a omecore:Image ;
         rdfs:label ?name ;
         omekg:ome_details ?viewer ;
         omekg:download ?thumbnail .
}
LIMIT 20
```

Each `?viewer` value is a clickable link to the IDR web viewer, e.g.
`https://idr.openmicroscopy.org/webclient/img_detail/1461/`

### Entity counts

```sparql
PREFIX omecore: <https://ld.openmicroscopy.org/core/>

SELECT ?type (COUNT(?entity) AS ?count)
WHERE {
  VALUES ?type {
    omecore:Image omecore:Dataset omecore:Project
    omecore:Screen omecore:Plate omecore:Well
  }
  ?entity a ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
```

### Organisms with image counts

This query traverses the structured annotation mappings to find all organisms
across the IDR and count the number of images per organism:

```sparql
PREFIX core: <https://ld.openmicroscopy.org/core/>

SELECT ?organism (COUNT(DISTINCT ?image) AS ?imageCount)
WHERE {
  ?image a core:Image .
  ?image core:hasAnnotation ?ann .
  ?ann a core:MapAnnotation .
  ?ann core:mapEntry ?entry .
  ?entry core:key ?key ;
         core:value ?organism .
  FILTER(LCASE(?key) = "organism")
}
GROUP BY ?organism
ORDER BY DESC(?imageCount)
```

The IDR contains 84 distinct organisms. The top results:

| Organism | Images |
|----------|-------:|
| Homo sapiens | 13,320,512 |
| Saccharomyces cerevisiae | 302,980 |
| SARS-CoV-2 | 143,810 |
| Mus musculus | 132,060 |

### Project-Dataset-Image hierarchy

```sparql
PREFIX omecore: <https://ld.openmicroscopy.org/core/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?project ?projectName ?dataset ?datasetName ?image ?imageName
WHERE {
  ?project a omecore:Project ;
           rdfs:label ?projectName ;
           dcterms:hasPart ?dataset .
  ?dataset a omecore:Dataset ;
           rdfs:label ?datasetName ;
           dcterms:hasPart ?image .
  ?image a omecore:Image ;
         rdfs:label ?imageName .
}
LIMIT 20
```

---

## Resolvable IRIs

A key feature of this deployment is that SPARQL results contain IRIs that
resolve to the live IDR web interface:

| Property | URL pattern | Description |
|----------|------------|-------------|
| Entity IRI | `https://idr.openmicroscopy.org/Image/{id}` | Stable identifier |
| `this:ome_details` | `.../webclient/img_detail/{id}/` | Full web viewer |
| `this:download` | `.../webgateway/render_image/{id}/` | PNG thumbnail |
| `this:json` | `.../api/v0/m/images/{id}/` | JSON API metadata |

This means any SPARQL client can render clickable links that take users
directly to the IDR viewer for any image in the result set.

---

## Lessons learned

Several issues were encountered and resolved during the IDR deployment. These
are instructive for anyone applying Ontop to large-scale databases:

1. **Meta-mappings and large tables do not mix.** Ontop's `<{map_key}>` syntax
   triggers `SELECT DISTINCT` on the source table at startup. With 86 million
   rows, the resulting PostgreSQL temp files can exhaust disk space. Use
   structured mappings (`core:mapEntry` / `core:key` / `core:value`) instead.

2. **Access control filters must match your deployment.** The upstream OMERO
   mappings assume a logged-in user context. For public data like the IDR,
   these filters return empty results and must be removed.

3. **JVM heap matters.** The default 512 MB heap is insufficient for large
   schemas. Set `ONTOP_JAVA_ARGS='-Xmx8g'` explicitly.

4. **The dump format is not what you expect.** The IDR dump is a `.tar.gz`
   wrapping a `pg_dump` directory format (with `toc.dat` + `*.dat.gz`). You
   must `tar xzf` first, then pass the extracted directory to `pg_restore`.

5. **Materialization takes hours, not minutes.** Budget ~6 hours for 1 billion
   triples. The gzipped output is manageable (4.9 GB), but ensure sufficient
   temp disk space during the process.

---

## Connection to earlier chapters

This chapter demonstrates the same three-file pattern used throughout the
tutorial:

| File | Solar system | OMERO | IDR |
|------|-------------|-------|-----|
| `.properties` | `solar_system.properties` | `omeswat.properties` | `idr.properties` |
| `.obda` | `solar_system.obda` | `omeswat.obda` | `idr.obda` |
| `.ttl` | `solar_system.ttl` | `omeswat.ttl` | `idr.ttl` |
| Triples | ~100 | ~thousands | **1,030,138,217** |

The workflow is identical at every scale — the same Ontop command, the same
mapping language, the same SPARQL protocol. Only the SQL queries, the RDF
templates, and the hardware requirements change.
