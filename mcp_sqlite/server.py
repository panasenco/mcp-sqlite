import argparse
import html
import logging
from pathlib import Path

import aiosqlite
import anyio
from mcp.server.fastmcp import FastMCP
import yaml


async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata: dict = {}) -> FastMCP:
    """Create a catalog of databases, tables, and columns that are actually in the connection, enriched with optional metadata."""
    server = FastMCP("mcp-sqlite", stateless_http=True, json_response=True)

    @server.resource("catalog://", mime_type="application/json")
    async def catalog() -> dict:
        # Copy all metadata except databases
        catalog = {key: value for key, value in metadata.items() if key != "databases"}
        # Initialize databases as an empty dict first
        catalog["databases"] = {}
        # Get the true database names and stems of their filepaths
        cursor = await sqlite_connection.execute("pragma database_list")
        for database_name, database_stem in [
            (database_row[1], Path(database_row[2]).stem) for database_row in await cursor.fetchall()
        ]:
            try:
                # Rename from the stem to the true SQLite-internal name (usually "main")
                database_dict = {
                    key: value for key, value in metadata["databases"][database_stem].items() if key != "tables"
                }
            except KeyError:
                database_dict = {}
            database_dict["tables"] = {}
            catalog["databases"][database_name] = database_dict
            # Get the table names
            cursor = await sqlite_connection.execute(f"pragma {database_name}.table_list")
            for table_name in [
                table_row[1] for table_row in await cursor.fetchall() if not table_row[1].startswith("sqlite_")
            ]:
                try:
                    table_dict = {
                        key: value
                        for key, value in metadata["databases"][database_stem]["tables"][table_name].items()
                        if key != "columns"
                    }
                except KeyError:
                    table_dict = {}
                # Omit hidden tables
                if "hidden" in table_dict and table_dict["hidden"] == True:
                    continue
                table_dict["columns"] = {}
                catalog["databases"][database_name]["tables"][table_name] = table_dict
                # Get the column names
                cursor = await sqlite_connection.execute(f"pragma {database_name}.table_info({table_name})")
                for column_name in [column_row[1] for column_row in await cursor.fetchall()]:
                    try:
                        column_description = metadata["databases"][database_stem]["tables"][table_name]["columns"][
                            column_name
                        ]
                    except KeyError:
                        column_description = ""
                    catalog["databases"][database_name]["tables"][table_name]["columns"][column_name] = (
                        column_description
                    )
        return catalog

    @server.tool()
    async def execute(sql: str) -> str:
        cursor = await sqlite_connection.execute(sql)
        header_inner_html = ""
        for column_description in cursor.description:
            header_inner_html += f"<th>{html.escape(column_description[0])}</th>"
        rows_html = f"<tr>{header_inner_html}</tr>"
        for row in await cursor.fetchall():
            row_inner_html = ""
            for value in row:
                row_inner_html += f"<td>{html.escape(str(value))}</td>"
            rows_html += f"<tr>{row_inner_html}</tr>"
        return f"<table>{rows_html}</table>"

    return server


async def main(sqlite_file: str, metadata_yaml_file: str | None = None):
    if metadata_yaml_file:
        with open(metadata_yaml_file, "r") as metadata_file_descriptor:
            metadata = yaml.safe_load(metadata_file_descriptor.read())
    else:
        metadata = {}
    async with aiosqlite.connect(f"file:{sqlite_file}", uri=True) as sqlite_connection:
        server = await mcp_sqlite_server(sqlite_connection=sqlite_connection, metadata=metadata)
        await server.run_stdio_async()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mcp-sqlite-server",
        description="CLI command to start an MCP server for interacting with SQLite data.",
    )
    parser.add_argument(
        "sqlite_file",
        help="Path to SQLite file to serve the MCP server for.",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        help="Path to Datasette-compatible metadata JSON file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose. Include once for INFO output, twice for DEBUG output.",
        action="count",
        default=0,
    )
    args = parser.parse_args()
    LOGGING_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=LOGGING_LEVELS[min(args.verbose, len(LOGGING_LEVELS) - 1)])  # cap to last level index
    anyio.run(main, args.sqlite_file, args.metadata)
