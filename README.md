# mcp-sqlite
Provide useful data to AI agents without giving them access to external systems. Compatible with Datasette for human users!


## Quickstart
1.  Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2.  Create or [download](https://github.com/davidjamesknight/SQLite_databases_for_learning_data_science/raw/refs/heads/main/titanic.db) a SQLite database file.
3.  Optionally create a metadata file for your dataset. See [Datasette metadata docs](https://docs.datasette.io/en/stable/metadata.html) for details.
4.  Create an entry in your MCP client for your database and metadata
    ```json
    {
        "mcpServers": {
            "sqlite": {
                "command": "uvx",
                "args": [
                    "mcp-sqlite",
                    "/absolute/path/to/database.db",
                    "--metadata",
                    "/absolute/path/to/metadata.yml"
                ]
            }
        }
    }
    ```

Your AI agent should now be able to use mcp-sqlite tools like `sqlite_get_catalog` and `sqlite_execute`!

### Exploring with MCP Inspector
Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) dashboard to interact with the SQLite database the same way that an AI agent would:
1.  Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
2.  Run:
    ```
    npx @modelcontextprotocol/inspector uvx mcp-sqlite path/to/database.db --metadata path/to/metadata.yml
    ```

### Exploring with Datasette
Since `mcp-sqlite` metadata is compatible with the Datasette metadata file, you can also explore your data with Datasette:
```
uvx datasette serve path/to/data.db --metadata path/to/metadata.yml
```
Compatibility with Datasette allows both AI agents and humans to easily explore the same local data!


## Motivation
As AI agents get smarter and more capable, the pressure to build and iterate AI-powered applications increases proportionally.
Malicious users can take advantage of AI agents' intelligence and access to access other users' data.
mcp-sqlite allows AI agents to have all the data they need in a local SQLite database, without any access to external systems.


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
                        Path to Datasette-compatible metadata JSON file.
  -w, --write           Set this flag to allow the AI agent to write to the database. By default the database is opened in read-only       
                        mode.
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
| [Write restrictions on canned queries](https://docs.datasette.io/en/stable/sql_queries.html#writable-canned-queries) | ❌ (planned) |
| [Magic parameters](https://docs.datasette.io/en/stable/sql_queries.html#magic-parameters) | ❌ (not planned) |
