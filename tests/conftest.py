import json
from pathlib import Path
import tempfile

import aiofiles
import aiosqlite
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import yaml
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def session_generator(statements, metadata, metadata_yaml=True):
    # Create the SQLite database file
    async with aiofiles.tempfile.NamedTemporaryFile(
        "w", prefix="mcp_sqlite_test_", suffix=".db", delete_on_close=False
    ) as db_file:
        await db_file.close()
        async with aiosqlite.connect(f"file:{db_file.name}", uri=True) as sqlite_connection:
            for statement in statements:
                await sqlite_connection.execute(statement)
            await sqlite_connection.commit()
        db_file_stem = Path(str(db_file.name)).stem
        # Create the metadata file
        metadata_suffix = ".yml" if metadata_yaml else ".json"
        with tempfile.NamedTemporaryFile(
            "w", prefix="mcp_sqlite_test_", suffix=metadata_suffix, delete_on_close=False
        ) as metadata_file:
            # Replace the database name with the actual one
            if "databases" in metadata:
                if "_" in metadata["databases"]:
                    metadata["databases"][db_file_stem] = metadata["databases"].pop("_")
            if metadata_yaml:
                yaml.dump(metadata, metadata_file, sort_keys=False)
            else:
                json.dump(metadata, metadata_file)
            metadata_file.close()
            # Create a stdio-connected client
            args = [
                "--directory",
                str(Path(__file__).parent.parent),
                "run",
                "mcp_sqlite/server.py",
                str(db_file.name),
                "--metadata",
                metadata_file.name,
            ]
            async with stdio_client(
                StdioServerParameters(
                    command="uv",
                    args=args,
                )
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield db_file_stem, session
            # Give time to the MCP server to exit before deleting the files
            await asyncio.sleep(1)


@pytest.fixture(scope="session")
async def empty_tuple():
    async for session_tuple in session_generator([], {}):
        yield session_tuple


@pytest.fixture(scope="session")
async def minimal_tuple():
    async for session_tuple in session_generator(
        [
            "create table table1 (col1, col2)",
        ],
        {},
    ):
        yield session_tuple


# Test small_tuple with both YAML and JSON metadata every time
@pytest.fixture(scope="session", params=[True, False])
async def small_tuple(request):
    async for session_tuple in session_generator(
        [
            "create table table1 (col1 primary key, col2)",
            "insert into table1 values (3, 'x')",
            "insert into table1 values (4, 'y')",
            "create table table2 (col3)",
            "insert into table2 values (false)",
            "create table table4 (col4)",
            "insert into table4 values (5)",
        ],
        {
            "title": "Index title",
            "license": "ODbL",
            "source_url": "http://example.com/",
            "databases": {
                "_": {
                    "source": "Alternative source",
                    "source_url": "http://example.com/",
                    "queries": {
                        "answer_to_life": {
                            "sql": "select 42",
                        }
                    },
                    "tables": {
                        "table2": {
                            "description": "Exists in the data, but will be hidden",
                            "sort": "col3",
                            "label_column": "col3",
                            "columns": {
                                "col3": "Third column",
                            },
                            "hidden": True,
                        },
                        "table1": {
                            "description_html": "Custom <em>table</em> description",
                            "license": "CC BY 3.0 US",
                            "license_url": "https://creativecommons.org/licenses/by/3.0/us/",
                            "columns": {
                                "col1": "Description of column 1",
                                "col2": "Description of column 2",
                                "nonexistent": "This column does not exist in the data",
                            },
                            "units": {
                                "col1": "metres",
                                "col2": "Hz",
                            },
                            "size": 10,
                            "sortable_columns": [
                                "col2",
                            ],
                        },
                        "table3": {
                            "description": "Does not exist in the data",
                        },
                    },
                }
            },
        },
        metadata_yaml=request.param,
    ):
        yield session_tuple


@pytest.fixture(scope="session")
async def canned_tuple():
    async for session_tuple in session_generator(
        [
            "create table table1 (col1 primary key, col2)",
            "insert into table1 values (3, 'x')",
            "insert into table1 values (4, 'y')",
            "create table table2 (col3)",
            "insert into table2 values (false)",
            "create table table4 (col4)",
            "insert into table4 values (5)",
        ],
        {
            "databases": {
                "_": {
                    "queries": {
                        "answer_to_life": {
                            "sql": "select 42",
                        },
                        "add_integers": {
                            "sql": "select :a + :b as total",
                        },
                        "descriptive": {
                            "title": "My useful title",
                            "description": "My description is so good the SQL can be omitted.",
                            "hide_sql": True,
                            "sql": "select null as this_should_not_appear_in_description",
                        },
                    },
                }
            },
        },
    ):
        yield session_tuple
