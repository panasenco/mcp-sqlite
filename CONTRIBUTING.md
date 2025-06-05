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