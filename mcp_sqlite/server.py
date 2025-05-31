from pathlib import Path

import aiosqlite
from mcp.server.fastmcp import FastMCP


async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata_yml_path: Path | None = None) -> FastMCP:
    server = FastMCP("mcp-sqlite", stateless_http=True, json_response=True)

    @server.resource("sqlite://", mime_type="application/json")
    def sqlite_resource() -> dict:
        return {"databases": []}

    return server
