# mcp-sqlite
Making local data equally accessible to AI agents and humans. Datasette-compatible!

## Usage
```
uvx mcp-sqlite path/to/data.db path/to/metadata.yml
```

## Datasette-compatible metadata
The `mcp-sqlite` metadata YAML file is based on the Datasette metadata file and is therefore completely compatible with it.
So you can also run:
```
uvx datasette serve path/to/data.db --metadata path/to/metadata.yml
```

### Canned queries
| Datasette canned query feature | Supported in mcp-sqlite? |
| ------------------------------ | ------------------------ |
| [Displayed in catalog](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Executable](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ✅ |
| [Titles](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ |
| [Descriptions](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ |
| [Parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ |
| [Explicit parameters](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries) | ❌ |
| [Hide SQL](https://docs.datasette.io/en/stable/sql_queries.html#hide-sql) | ❌ |
| [Fragments](https://docs.datasette.io/en/stable/sql_queries.html#fragment) | ❌ |
| [Write restrictions on canned queries](https://docs.datasette.io/en/stable/sql_queries.html#writable-canned-queries) | ❌ |
| [Magic parameters](https://docs.datasette.io/en/stable/sql_queries.html#magic-parameters) | ❌ |

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