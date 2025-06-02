import argparse
import html
import logging
from pathlib import Path
import re

import aiosqlite
import anyio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import yaml

class TableMetadata(BaseModel):
    hidden: bool = False
    columns: dict[str, str] = Field(default_factory=dict)
    model_config = {
        "extra": "allow",
    }

class DatabaseMetadata(BaseModel):
    tables: dict[str, TableMetadata] = Field(default_factory=dict)
    model_config = {
        "extra": "allow",
    }

class RootMetadata(BaseModel):
    databases: dict[str, DatabaseMetadata] = Field(default_factory=dict)
    model_config = {
        "extra": "allow",
    }


async def get_catalog(sqlite_connection: aiosqlite.Connection, metadata: RootMetadata) -> RootMetadata:
    # Copy all metadata except databases
    catalog = RootMetadata(**{key: value for key, value in metadata if key != "databases"})
    # Get the true database names and stems of their filepaths
    cursor = await sqlite_connection.execute("pragma database_list")
    for database_name, database_stem in [
        (database_row[1], Path(database_row[2]).stem) for database_row in await cursor.fetchall()
    ]:
        database_in_metadata = database_stem in metadata.databases
        # Rename from the stem to the true SQLite-internal name (usually "main")
        database = DatabaseMetadata(**({key: value for key, value in metadata.databases[database_stem] if key != "tables"} if database_in_metadata else {}))
        # Get the table names
        cursor = await sqlite_connection.execute(f"pragma {database_name}.table_list")
        for table_name in [
            table_row[1] for table_row in await cursor.fetchall() if not table_row[1].startswith("sqlite_")
        ]:
            table_in_metadata = database_in_metadata and table_name in metadata.databases[database_stem].tables
            table = TableMetadata(**({
                key: value
                for key, value in metadata.databases[database_stem].tables[table_name]
                if key != "columns"
            } if table_in_metadata else {}))
            # Omit hidden tables
            if table.hidden:
                continue
            # Get the column names
            cursor = await sqlite_connection.execute(f"pragma {database_name}.table_info({table_name})")
            for column_name in [column_row[1] for column_row in await cursor.fetchall()]:
                column_in_metadata = table_in_metadata and column_name in metadata.databases[database_stem].tables[table_name].columns
                column_description = metadata.databases[database_stem].tables[table_name].columns[column_name] if column_in_metadata else ""
                table.columns[column_name] = column_description
            database.tables[table_name] = table
        catalog.databases[database_name] = database
    return catalog

async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata: RootMetadata = RootMetadata()) -> FastMCP:
    """Create a catalog of databases, tables, and columns that are actually in the connection, enriched with optional metadata."""
    server = FastMCP("mcp-sqlite", stateless_http=True, json_response=True)

    @server.resource("catalog://", mime_type="application/json")
    async def catalog() -> RootMetadata:
        return await get_catalog(sqlite_connection=sqlite_connection, metadata=metadata)

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

    # initial_catalog = await get_catalog(sqlite_connection=sqlite_connection, metadata=metadata)
    # for database in initial_catalog.databases:
    #     if not isinstance(initial_catalog["databases"][database], dict):
    #         continue

    #     try:
    #         if "queries" in initial_catalog["databases"][database]:
    #             pass
    #     except TypeError:
    #         pass
    #     for query in initial_catalog["databases"][database]["queries"]:
    #         query_slug = re.sub("[^a-z]+", "_", query["title"].lower())
    #         @server.tool(name=f"execute_{database}_{query_slug}")
    #         async def execute_canned_query() -> str:
    #             await execute(sql=query["sql"])

    return server


async def main(sqlite_file: str, metadata_yaml_file: str | None = None):
    if metadata_yaml_file:
        with open(metadata_yaml_file, "r") as metadata_file_descriptor:
            metadata_dict = yaml.safe_load(metadata_file_descriptor.read())
    else:
        metadata_dict = {}
    async with aiosqlite.connect(f"file:{sqlite_file}", uri=True) as sqlite_connection:
        server = await mcp_sqlite_server(sqlite_connection=sqlite_connection, metadata=RootMetadata(**metadata_dict))
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
