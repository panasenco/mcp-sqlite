import json

import aiosqlite
import pytest

from mcp_sqlite.server import mcp_sqlite_server


@pytest.fixture
async def empty_server():
    async with aiosqlite.connect("file::memory:", uri=True) as sqlite_connection:
        yield await mcp_sqlite_server(sqlite_connection)


@pytest.mark.anyio
async def test_settings(empty_server):
    # The server should be stateless and return JSON
    assert empty_server.settings.stateless_http
    assert empty_server.settings.json_response


@pytest.mark.anyio
async def test_resource(empty_server):
    # There should be only one resource that returns the entire structure of the database
    assert [str(resource.uri) for resource in await empty_server.list_resources()] == ["sqlite://"]
    assert len(await empty_server.list_resource_templates()) == 0
    resources = await empty_server.read_resource("sqlite://")
    assert len(resources) == 1
    assert resources[0].mime_type == "application/json"
    assert json.loads(resources[0].content) == {"databases": []}
