# mcp-sqlite
Provide useful data to AI agents without giving them access to external systems. Datasette-compatible!

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
3.  Open the MCP Inspector dashboard URL that's outputted in your terminal window.

### Exploring with Datasette
Since `mcp-sqlite` metadata is compatible with the Datasette metadata file, you can also explore your data with Datasette:
```
uvx datasette serve path/to/data.db --metadata path/to/metadata.yml
```

## MCP Tools provided by mcp-sqlite
- **sqlite_get_catalog()**: Tool the agent can call to get the complete catalog of the databases, tables, and columns in the data, combined with metadata from the metadata file. In an earlier iteration of `mcp-sqlite`, this was a resource instead of a tool, but resources are not as widely supported, so it got turned into a tool. If you have a usecase for the catalog as a resource, open an issue and we'll bring it back!
- **sqlite_execute(sql)**: Tool the agent can call to execute arbitrary SQL. The table results are returned as HTML, as that is the format LLMs seem to perform best with according to [Siu et al](https://arxiv.org/abs/2305.13062).
- **sqlite_execute_main_{canned query name}({canned query args})**: A tool is created for each canned query in the metadata, allowing the agent to run predefined queries without writing any SQL.

## Usage

### Command-line options
```
usage: mcp-sqlite-server [-h] [-m METADATA] [-w] [-v] sqlite_file

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
[Hiding a table](https://docs.datasette.io/en/stable/metadata.html#hiding-tables) with `hidden: true` will hide it from the catalog returned by the `get_catalog()` MCP tool.
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
| [Titles](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ (planned) |
| [Descriptions](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ (planned) |
| [Parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Explicit parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ (planned) |
| [Hide SQL](https://docs.datasette.io/en/stable/sql_queries.html#hide-sql) | ❌ (planned) |
| [Fragments](https://docs.datasette.io/en/stable/sql_queries.html#fragment) | ❌ (not planned) |
| [Write restrictions on canned queries](https://docs.datasette.io/en/stable/sql_queries.html#writable-canned-queries) | ❌ (planned) |
| [Magic parameters](https://docs.datasette.io/en/stable/sql_queries.html#magic-parameters) | ❌ (not planned) |

This will open up a Datasette dashboard where you can see the exact same descriptions and sample queries that the LLM would see.
Compatibility with Datasette allows both humans and AI to interact with the same local data!

## Developing
1.  Clone this repo locally.
2.  Run `uv venv` to create the Python virtual environment.
    Then run `source .venv/bin/activate` on Unix or `.venv\Scripts\activate` on Windows.
3.  Run the server with [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
    (you'll have to [install Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) first):
    ```
    npx @modelcontextprotocol/inspector uv run mcp_sqlite/server.py test.db --metadata test.yml
    ```

- Run `python -m pytest` to run tests.
- Run `ruff format` to format Python code.
- Run `pyright` for static type checking.

### Publishing
- Tagging a commit with a release candidate tag (containing `rc`) will trigger build and upload to TestPyPi.
  - Note that Python package version numbers are NOT SemVer! See [Python packaging versioning](https://packaging.python.org/en/latest/discussions/versioning/).
  - To test that the package works on TestPyPi, use: `uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ mcp-sqlite@0.1.0rc2 --help` (replacing `0.1.0rc2` with your own version number).
  - Similarly, to test the TestPyPi package with MCP inspector, use: `npx @modelcontextprotocol/inspector uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ mcp-sqlite@0.1.0rc2 test.db --metadata test.yml`.
- Tagging a commit with a non-release candidate tag (not containing `rc`) will trigger build and upload to PyPi.