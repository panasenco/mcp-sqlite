import logging
from pathlib import Path
import tempfile
import time

import aiofiles
import aiosqlite
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import yaml
import pytest

from mcp_sqlite.server import mcp_sqlite_server


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def empty_server():
    async with aiosqlite.connect("file::memory:", uri=True) as sqlite_connection:
        yield await mcp_sqlite_server(sqlite_connection)


@pytest.fixture
async def minimal_server():
    async with aiosqlite.connect("file::memory:", uri=True) as sqlite_connection:
        await sqlite_connection.execute("create table table1 (col1, col2)")
        await sqlite_connection.commit()
        yield await mcp_sqlite_server(sqlite_connection)


@pytest.fixture
async def small_sqlite_file():
    async with aiofiles.tempfile.NamedTemporaryFile(
        "w", prefix="mcp_sqlite_test_small_", suffix=".db", delete_on_close=False
    ) as db_file:
        await db_file.close()
        async with aiosqlite.connect(f"file:{db_file.name}", uri=True) as sqlite_connection:
            await sqlite_connection.execute("create table table1 (col1 primary key, col2)")
            await sqlite_connection.execute("insert into table1 values (3, 'x')")
            await sqlite_connection.execute("insert into table1 values (4, 'y')")
            await sqlite_connection.execute("create table table2 (col3)")
            await sqlite_connection.execute("insert into table2 values (false)")
            await sqlite_connection.execute("create table table4 (col4)")
            await sqlite_connection.execute("insert into table4 values (5)")
            await sqlite_connection.commit()
        logging.debug(f"small_sqlite_file: {db_file.name}")
        yield db_file.name
        # Give time to the MCP server to exit before deleting the SQLite file
        await asyncio.sleep(1)


@pytest.fixture
def small_metadata_file(small_sqlite_file):
    with tempfile.NamedTemporaryFile(
        "w", prefix="mcp_sqlite_test_small_", suffix=".yml", delete_on_close=False
    ) as metadata_file:
        yaml.dump(
            {
                "title": "Index title",
                "license": "ODbL",
                "source_url": "http://example.com/",
                "databases": {
                    Path(small_sqlite_file).stem: {
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
            metadata_file,
            sort_keys=False,
        )
        metadata_file.close()
        yield metadata_file.name
        # Give time to the MCP server to exit before deleting the SQLite file
        time.sleep(1)


@pytest.fixture
async def small_server(small_sqlite_file, small_metadata_file):
    async with aiofiles.open(small_metadata_file, mode="r") as metadata_file_descriptor:
        metadata = yaml.safe_load(await metadata_file_descriptor.read())
    async with aiosqlite.connect(f"file:{small_sqlite_file}", uri=True) as sqlite_connection:
        yield await mcp_sqlite_server(sqlite_connection, metadata)


@pytest.fixture
async def small_client_session(small_sqlite_file, small_metadata_file):
    async with stdio_client(
        StdioServerParameters(
            command="uv",
            args=[
                "--directory",
                str(Path(__file__).parent.parent),
                "run",
                "mcp_sqlite/server.py",
                small_sqlite_file,
                "--meta",
                small_metadata_file,
            ],
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


@pytest.fixture
def canned_queries_metadata_file(small_sqlite_file):
    with tempfile.NamedTemporaryFile(
        "w", prefix="mcp_sqlite_test_canned_queries_", suffix=".yml", delete_on_close=False
    ) as metadata_file:
        yaml.dump(
            {
                "databases": {
                    Path(small_sqlite_file).stem: {
                        "queries": {
                            "answer_to_life": {
                                "title": "Answer to life",
                                "sql": "select 42",
                            }
                        },
                    }
                },
            },
            metadata_file,
            sort_keys=False,
        )
        metadata_file.close()
        yield metadata_file.name
        # Give time to the MCP server to exit before deleting the SQLite file
        time.sleep(1)


@pytest.fixture
async def canned_queries_client_session(small_sqlite_file, canned_queries_metadata_file):
    async with stdio_client(
        StdioServerParameters(
            command="uv",
            args=[
                "--directory",
                str(Path(__file__).parent.parent),
                "run",
                "mcp_sqlite/server.py",
                small_sqlite_file,
                "--meta",
                canned_queries_metadata_file,
            ],
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
