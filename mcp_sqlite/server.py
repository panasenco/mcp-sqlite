from pathlib import Path

import aiosqlite
from mcp.server.fastmcp import FastMCP


async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata: dict | None = None) -> FastMCP:
    server = FastMCP("mcp-sqlite", stateless_http=True, json_response=True)

    @server.resource("sqlite://", mime_type="application/json")
    async def sqlite_resource() -> dict:
        cursor = await sqlite_connection.execute("pragma database_list")
        database_names_stems = [
            (database_row[1], Path(database_row[2]).stem) for database_row in await cursor.fetchall()
        ]
        resource = {"databases": {}}
        for database_name, database_stem in database_names_stems:
            resource["databases"][database_name] = {"tables": {}}
            cursor = await sqlite_connection.execute(f"pragma {database_name}.table_list")
            table_names = [
                table_row[1] for table_row in await cursor.fetchall() if not table_row[1].startswith("sqlite_")
            ]
            for table_name in table_names:
                cursor = await sqlite_connection.execute(f"pragma {database_name}.table_info({table_name})")
                resource["databases"][database_name]["tables"][table_name] = {
                    "columns": {
                        column_name: "" for column_name in [column_row[1] for column_row in await cursor.fetchall()]
                    }
                }
        return resource

    return server
