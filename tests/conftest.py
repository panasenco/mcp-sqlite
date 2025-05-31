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
