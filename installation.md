---
title: "Installation"
---

# Installation

This tutorial supports two execution modes. The table below shows which
components are needed for each:

| Component | CLI mode | GraphDB Desktop mode |
|-----------|:--------:|:--------------------:|
| Java 17+  | ✅ | ✅ |
| Ontop CLI | ✅ | optional |
| DuckDB    | optional | ✅ |
| GraphDB Desktop | ❌ | ✅ |
| DuckDB JDBC driver | ❌ | ✅ |

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

---

## 3. DuckDB (GraphDB mode and optional CLI mode)

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

## 4. GraphDB Desktop (optional — Desktop mode only)

Download from [https://www.ontotext.com/products/graphdb/](https://www.ontotext.com/products/graphdb/)
and follow the vendor's installation instructions.

After installation, start GraphDB and open the Workbench at:
[http://localhost:7200](http://localhost:7200)

---

## 5. DuckDB JDBC Driver (GraphDB Desktop mode only)

GraphDB's embedded Ontop needs the DuckDB JDBC driver to connect to a
DuckDB database.

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

## Tested versions

| Software | Tested version |
|----------|---------------|
| Ontop CLI | 5.5.x |
| GraphDB Desktop | 10.4.x |
| DuckDB | 0.10.x |
| Java | 17+ |
