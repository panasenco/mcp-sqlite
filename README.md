# mcp-sqlite
<p align="center">
  <img src="https://github.com/panasenco/mcp-sqlite/raw/main/images/mcp-sqlite-256.png">
</p>

Provide useful data to AI agents without giving them access to external systems. Compatible with Datasette for human users!

## Features
- AI agents can get the structure of all tables and columns in the SQLite database in one command - `sqlite_get_catalog`.
  - The catalog can be enriched with descriptions for the tables and columns using a simple YAML or JSON metadata file.
- The same metadata file can contain canned queries to the AI to use.
  Each canned query will be turned into a separate MCP tool `sqlite_execute_main_{tool name}`.
- AI agents can execute arbitrary SQL queries with `sqlite_execute`.


## Quickstart
1.  Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2.  Download the sample SQLite database [titanic.db](https://github.com/davidjamesknight/SQLite_databases_for_learning_data_science/raw/refs/heads/main/titanic.db).
3.  Create a metadata file `titanic.yml` for your dataset:
    ```yaml
    databases:
      titanic:
        tables:
          Observation:
            description: Main table connecting passenger attributes to observed outcomes.
            columns:
              survived: "0/1 indicator whether the passenger survived."
              age: The passenger's age at the time of the crash.
              # Other columns are not documented but are still visible to the AI agent
        queries:
          survivors_of_age:
            title: Count survivors of a specific age
            description: Returns the total counts of passengers and survivors, both for all ages and for a specific provided age.
            sql: |-
              select
                count(*) as total_passengers,
                sum(survived) as survived_passengers,
                sum(case when age = :age then 1 else 0 end) as total_specific_age,
                sum(case when age = :age and survived = 1 then 1 else 0 end) as survived_specific_age
              from Observation
    ```
4.  Create an entry in your MCP client for your database and metadata
    ```json
    {
        "mcpServers": {
            "sqlite": {
                "command": "uvx",
                "args": [
                    "mcp-sqlite",
                    "/absolute/path/to/titanic.db",
                    "--metadata",
                    "/absolute/path/to/titanic.yml"
                ]
            }
        }
    }
    ```

Your AI agent should now be able to use mcp-sqlite tools `sqlite_get_catalog`, `sqlite_execute`, and `sqlite_execute_main_survivors_of_age`!

## Interactive exploration with MCP Inspector and Datasette

The same database and metadata files can be used to explore the data interactively with MCP Inspector and Datasette.

| MCP Inspector | Datasette |
| ------------- | --------- |
| ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/mcp-inspector-sqlite-get-catalog.png) | ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/datasette-table-view.png) |
| ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/mcp-inspector-sqlite-canned-query-tool.png) | ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/datasette-canned-query.png) |

### MCP Inspector
Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) dashboard to interact with the SQLite database the same way that an AI agent would:
1.  Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
2.  Run:
    ```
    npx @modelcontextprotocol/inspector uvx mcp-sqlite path/to/titanic.db --metadata path/to/titanic.yml
    ```

### Datasette
Since `mcp-sqlite` metadata is compatible with the Datasette metadata file, you can also explore your data with Datasette:
```
uvx datasette serve path/to/titanic.db --metadata path/to/titanic.yml
```
Compatibility with Datasette allows both AI agents and humans to easily explore the same local data!


## MCP Tools provided by mcp-sqlite
- **sqlite_get_catalog()**: Tool the agent can call to get the complete catalog of the databases, tables, and columns in the data, combined with metadata from the metadata file.
  In an earlier iteration of `mcp-sqlite`, this was a resource instead of a tool, but resources are not as widely supported, so it got turned into a tool.
  If you have a usecase for the catalog as a resource, open an issue and we'll bring it back!
- **sqlite_execute(sql)**: Tool the agent can call to execute arbitrary SQL. The table results are returned as HTML.
  For more information about why HTML is the best format for LLMs to process, see [Siu et al](https://arxiv.org/abs/2305.13062).
- **sqlite_execute_main_{canned query name}({canned query args})**: A tool is created for each canned query in the metadata, allowing the agent to run predefined queries without writing any SQL.


## Usage

### Command-line options
```
usage: mcp-sqlite [-h] [-m METADATA] [-w] [-v] sqlite_file

CLI command to start an MCP server for interacting with SQLite data.

positional arguments:
  sqlite_file           Path to SQLite file to serve the MCP server for.

options:
  -h, --help            show this help message and exit
  -m METADATA, --metadata METADATA
                        Path to Datasette-compatible metadata YAML or JSON file.
  -w, --write           Set this flag to allow the AI agent to write to the database. By default the database is opened in read-only mode.
  -v, --verbose         Be verbose. Include once for INFO output, twice for DEBUG output.
```

### Metadata

#### Hidden tables
[Hiding a table](https://docs.datasette.io/en/stable/metadata.html#hiding-tables) with `hidden: true` will hide it from the catalog returned by the MCP tool `sqlite_get_catalog()`.
However, note that the table will still be accessible by the AI agent!
Never rely on hiding a table from the catalog as a security feature.

#### Canned queries
[Canned queries](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) are each turned into a separate callable MCP tool by mcp-sqlite.

For example, a query named `my_canned_query` will become a tool `sqlite_execute_main_my_canned_query`.

The canned queries functionality is still in active development with more features planned for development soon:

| Datasette canned query feature | Supported in mcp-sqlite? |
| ------------------------------ | ------------------------ |
| [Displayed in catalog](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Executable](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Titles](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Descriptions](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Explicit parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ (planned) |
| [Hide SQL](https://docs.datasette.io/en/stable/sql_queries.html#hide-sql) | ✅ |
| [Fragments](https://docs.datasette.io/en/stable/sql_queries.html#fragment) | ❌ (not planned) |
| [Write restrictions on canned queries](https://docs.datasette.io/en/stable/sql_queries.html#writable-canned-queries) | ✅ |
| [Magic parameters](https://docs.datasette.io/en/stable/sql_queries.html#magic-parameters) | ❌ (not planned) |
