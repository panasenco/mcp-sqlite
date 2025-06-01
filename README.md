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

This will open up a Datasette dashboard where you can see the exact same descriptions and sample queries that the LLM would see.
Compatibility with Datasette allows both humans and AI to interact with the same local data!

## Developing
1.  Clone this repo locally.
2.  Run `uv venv` to create the Python virtual environment.
    Then run `source .venv/bin/activate` on Unix or `.venv\Scripts\activate` on Windows.
3.  Run the server with [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
    (you'll have to [install Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) first):
    ```
    npx @modelcontextprotocol/inspector uv run mcp_sqlite
    ```

- Run `python -m pytest` to run tests.
- Run `ruff format` to format Python code.
- Run `pyright` for static type checking.