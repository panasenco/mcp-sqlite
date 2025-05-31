from pathlib import Path

import aiosqlite
from mcp.server.fastmcp import FastMCP


async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata: dict | None = None) -> FastMCP:
    server = FastMCP("mcp-sqlite", stateless_http=True, json_response=True)

    @server.resource("sqlite://", mime_type="application/json")
    async def sqlite_resource() -> dict:
        cursor = await sqlite_connection.execute("pragma database_list")
        return {
            "databases": {
                (Path(database_list[2]).stem or database_list[1]): {"tables": {}}
                for database_list in await cursor.fetchall()
            }
        }

    return server
