---
title: "CLI SPARQL Endpoint"
---

# CLI SPARQL Endpoint

The Ontop CLI mode starts a **live SPARQL endpoint** that reads OMOP Parquet
files directly — no separate database server is required.

---

## Prerequisites

- Java 17+ installed and on your PATH
- Ontop CLI installed and on your PATH (see [Installation](installation.md))
- The repository cloned locally

---

## Start the endpoint

From the root of the cloned repository, run:

::::{tab-set}
:::{tab-item} macOS / Linux
```bash
ontop endpoint \
    --ontology ontology/OMOP.ttl \
    --mapping mappings/OMOP-parquet.obda \
    --properties mappings/OMOP.properties \
    --port=8081
```
:::
:::{tab-item} Windows (PowerShell)
```powershell
ontop.bat endpoint `
    --ontology ontology/OMOP.ttl `
    --mapping mappings/OMOP-parquet.obda `
    --properties mappings/OMOP.properties `
    --port=8081
```
:::
::::

:::{note}
The Parquet files must be present in the `data/` directory.
Ontop resolves the `read_parquet('file.parquet')` paths relative to the
working directory where you run the command. Run from the repository root,
or adjust the paths in the mapping file accordingly.
:::

---

## Verify the endpoint

Once Ontop has started you should see output similar to:

```
[main] INFO  - Ontop is ready to accept SPARQL queries at http://localhost:8081/sparql
```

Open the **SPARQL Workbench** in your browser:

[http://localhost:8081](http://localhost:8081)

You can type SPARQL queries directly in the web interface.

---

## Optional: allow cross-origin requests (YASGUI)

If you want to use an external SPARQL client such as YASGUI, add the
CORS flag:

```bash
ontop endpoint \
    --ontology ontology/OMOP.ttl \
    --mapping mappings/OMOP-parquet.obda \
    --properties mappings/OMOP.properties \
    --port=8081 \
    --cors-allowed-origins=http://yasgui.org
```

---

## Command reference

| Flag | Description |
|------|-------------|
| `--ontology` | Path to the OWL ontology file (`.ttl`) |
| `--mapping` | Path to the OBDA mapping file (`.obda`) |
| `--properties` | Path to the JDBC properties file (`.properties`) |
| `--port` | Port number for the SPARQL endpoint (default: 8080) |
| `--cors-allowed-origins` | Allowed CORS origins for cross-domain access |

---

## Stopping the endpoint

Press `Ctrl+C` in the terminal to stop the Ontop process.
