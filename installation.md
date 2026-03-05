---
title: "Installation"
---

# Installation

This tutorial covers multiple use cases with different database backends.
The table below shows which components are needed for each:

| Component | Solar system / OMERO | OMOP CDM | GBIF | GraphDB mode |
|-----------|:-------------------:|:--------:|:----:|:------------:|
| Java 17+  | required | required | required | required |
| Ontop CLI | required | required | required | optional |
| PostgreSQL client | required | — | — | — |
| DuckDB | — | required | required | optional |
| Python 3 + rdflib + pandas | warmup chapter | — | — | — |
| Apache Jena (`arq`) | warmup chapter | — | — | — |
| GraphDB Desktop | — | — | — | required |
| DuckDB JDBC driver | — | — | — | required |
| AWS CLI | — | — | for extraction | — |

---

## 1. Java 17+

Check whether Java is already installed:

```bash
java -version
```

You should see version **17 or higher**. If not, install it:

::::{tab-set}
:::{tab-item} macOS (Homebrew)
```bash
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk \
    /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```
:::
:::{tab-item} Ubuntu / Debian
```bash
sudo apt update
sudo apt install openjdk-17-jdk
```
:::
:::{tab-item} Windows
Download OpenJDK 17 from [https://adoptium.net/](https://adoptium.net/).
After installation open a new terminal and verify:
```bash
java -version
```
:::
::::

---

## 2. Ontop CLI

Ontop CLI is the core component that powers the SPARQL endpoint.

1. Download the latest **5.x CLI** distribution from
   [https://ontop-vkg.org/download/](https://ontop-vkg.org/download/)
2. Unzip the archive:
   ```bash
   unzip ontop-cli-5.x.zip
   ```
3. Add the `bin` directory to your PATH:

::::{tab-set}
:::{tab-item} macOS / Linux
```bash
export PATH=$PATH:/path/to/ontop-cli-5.x/bin
```
Add this line to your `~/.zshrc` or `~/.bashrc` to make it permanent.
:::
:::{tab-item} Windows
Add the `bin` directory to your **System PATH** via Environment Variables.
:::
::::

4. Verify the installation:
   ```bash
   ontop version
   ```
   Expected output: `Ontop version 5.x`

### JDBC drivers

Place the appropriate JDBC driver `.jar` files in the Ontop `jdbc/` directory:

- **PostgreSQL** (for solar system and OMERO): Download from
  [https://jdbc.postgresql.org/download/](https://jdbc.postgresql.org/download/)
- **DuckDB** (for OMOP and GBIF): Download from
  [https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/](https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/)

---

## 3. Python 3 with rdflib and pandas (warmup chapter)

The warmup exercise uses Python to convert CSV data to RDF:

```bash
pip install rdflib pandas
```

---

## 4. Apache Jena — `arq` (warmup chapter)

`arq` is a command-line SPARQL query tool for testing RDF files locally:

1. Download Apache Jena from [https://jena.apache.org/download/](https://jena.apache.org/download/)
2. Unzip and add the `bin/` directory to your PATH

Verify:

```bash
arq --version
```

---

## 5. DuckDB (OMOP and GBIF use cases)

::::{tab-set}
:::{tab-item} macOS
```bash
brew install duckdb
```
:::
:::{tab-item} Ubuntu
```bash
sudo apt install duckdb
```
:::
:::{tab-item} Windows
Download from [https://duckdb.org/docs/installation/](https://duckdb.org/docs/installation/)
:::
::::

Verify:

```bash
duckdb --version
```

---

## 6. GraphDB Desktop (optional — Desktop mode only)

Download from [https://www.ontotext.com/products/graphdb/](https://www.ontotext.com/products/graphdb/)
and follow the vendor's installation instructions.

After installation, start GraphDB and open the Workbench at:
[http://localhost:7200](http://localhost:7200)

### DuckDB JDBC driver for GraphDB

GraphDB's embedded Ontop needs the DuckDB JDBC driver:

1. Download the driver `.jar` from:
   [https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/](https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/)
2. Place it in the GraphDB `lib/ext` directory:

   | OS | Path |
   |----|------|
   | macOS | `GraphDB.app/Contents/app/lib/ext/` |
   | Linux | `graphdb/lib/ext/` |
   | Windows | `graphdb\lib\ext\` |

3. **Restart GraphDB** after placing the driver.

---

## 7. AWS CLI (GBIF extraction only)

The GBIF chapter uses the AWS CLI to list S3 bucket contents. No AWS
account or credentials are needed — the GBIF bucket is public.

::::{tab-set}
:::{tab-item} macOS
```bash
brew install awscli
```
:::
:::{tab-item} Ubuntu
```bash
sudo apt install awscli
```
:::
:::{tab-item} Windows
Download from [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)
:::
::::

---

## Tested versions

| Software | Tested version |
|----------|---------------|
| Ontop CLI | 5.4.x / 5.5.x |
| GraphDB Desktop | 10.4.x |
| DuckDB | 0.10.x |
| Java | 17+ |
| Python | 3.10+ |
| Apache Jena | 4.x / 5.x |
| PostgreSQL | 14+ |
