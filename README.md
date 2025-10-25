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


## Quickstart using Visual Studio Code
1.  Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2.  Install [Visual Studio Code](https://code.visualstudio.com) if you don't already have it.
    Turn on GitHub Copilot.
3.  Open this repo in VS Code.
    Open a GitHub Copilot agent mode chat.
    Check the available tools - you should see MCP Server: sqlite_sample with three available tools.

    ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/vs-code-mcp-sqlite-sample.png)
4.  You should be able to ask Copilot in agent mode a question like "Get Titanic survivors of age 28" and get a response.

    ![](https://github.com/panasenco/mcp-sqlite/raw/main/images/github-copilot-agent-mode-sample.png)
5.  Use the sample MCP configuration file [mcp.json](.vscode/mcp.json) and the sample metadata file
    [titanic.yml](sample/titanic.yml) as a starting point for your own configuration.


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
- **{canned query name}({canned query args})**: A tool is created for each canned query in the metadata, allowing the agent to run predefined queries without writing any SQL.


## Usage

### Command-line options
```
usage: mcp-sqlite [-h] -m METADATA [-p PREFIX] [-v] sqlite_file

CLI command to start an MCP server for interacting with SQLite data.

positional arguments:
  sqlite_file           Path to SQLite file to serve the MCP server for.

options:
  -h, --help            show this help message and exit
  -m METADATA, --metadata METADATA
                        Path to Datasette-compatible metadata YAML or JSON file.
  -p PREFIX, --prefix PREFIX
                        Prefix for MCP tools. Defaults to no prefix.
  -v, --verbose         Be verbose. Include once for INFO output, twice for DEBUG output.
```

### Metadata

#### Hidden tables
[Hiding a table](https://docs.datasette.io/en/stable/metadata.html#hiding-tables) with `hidden: true` will hide it from the catalog returned by the MCP tool `sqlite_get_catalog()`.
However, note that the table will still be accessible by the AI agent!
Never rely on hiding a table from the catalog as a security feature.

#### Canned queries
[Canned queries](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) are each turned into a separate callable MCP tool by mcp-sqlite.

For example, a query named `my_canned_query` will become a tool `my_canned_query`.

The canned queries functionality is still in active development with more features planned for development soon:

## Roadmap

| Datasette query feature | Supported in mcp-sqlite? |
| ------------------------------ | ------------------------ |
| [Displayed in catalog](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Executable](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Titles](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Descriptions](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Explicit parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ (planned) |
| [Hide SQL](https://docs.datasette.io/en/stable/sql_queries.html#hide-sql) | ✅ |
| [Write restrictions on canned queries](https://docs.datasette.io/en/stable/sql_queries.html#writable-canned-queries) | ✅ |
| [Pagination](https://docs.datasette.io/en/stable/sql_queries.html#pagination) | ❌ (planned) |
| [Cross-database queries](https://docs.datasette.io/en/stable/sql_queries.html#cross-database-queries) | ❌ (planned) |
| [Fragments](https://docs.datasette.io/en/stable/sql_queries.html#fragment) | ❌ (not planned) |
| [Magic parameters](https://docs.datasette.io/en/stable/sql_queries.html#magic-parameters) | ❌ (not planned) |
