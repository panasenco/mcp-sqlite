from pathlib import Path
import tempfile

import aiosqlite
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
async def small_metadata_server():
    with tempfile.NamedTemporaryFile("w", prefix="mcp_sqlite_test_", suffix=".db", delete_on_close=False) as db_file:
        async with aiosqlite.connect(f"file:{db_file.name}", uri=True) as sqlite_connection:
            await sqlite_connection.execute("create table table1 (col1 primary key, col2)")
            await sqlite_connection.execute("insert into table1 values (3, 'x')")
            await sqlite_connection.execute("insert into table1 values (4, 'y')")
            await sqlite_connection.execute("create table table2 (col3)")
            await sqlite_connection.execute("insert into table2 values (false)")
            await sqlite_connection.execute("create table table4 (col4)")
            await sqlite_connection.execute("insert into table4 values (5)")
            await sqlite_connection.commit()
            yield await mcp_sqlite_server(
                sqlite_connection,
                {
                    "title": "Index title",
                    "license": "ODbL",
                    "source_url": "http://example.com/",
                    "databases": {
                        Path(db_file.name).stem: {
                            "source": "Alternative source",
                            "source_url": "http://example.com/",
                            "queries": {
                                "answer_to_life": "select 42",
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
            )
