import json

import pytest


@pytest.mark.anyio
async def test_settings(empty_server):
    # The server should be stateless and return JSON
    assert empty_server.settings.stateless_http


@pytest.mark.anyio
async def test_server_empty_catalog(empty_server):
    assert len(await empty_server.list_tools()) > 0
    responses = await empty_server.call_tool("get_catalog", {})
    assert len(responses) == 1
    assert json.loads(responses[0].text) == {"databases": {"main": {"queries": {}, "tables": {}}}}


@pytest.mark.anyio
async def test_server_minimal_catalog(minimal_server):
    # There should be only one resource that returns the entire catalog of the SQLite connection
    responses = await minimal_server.call_tool("get_catalog", {})
    assert len(responses) == 1
    assert json.loads(responses[0].text) == {
        "databases": {
            "main": {
                "queries": {},
                "tables": {
                    "table1": {
                        "columns": {
                            "col1": "",
                            "col2": "",
                        }
                    }
                },
            },
        },
    }


EXPECTED_SMALL_CATALOG = {
    "title": "Index title",
    "license": "ODbL",
    "source_url": "http://example.com/",
    "databases": {
        "main": {
            "source": "Alternative source",
            "source_url": "http://example.com/",
            "queries": {
                "answer_to_life": {
                    "sql": "select 42",
                }
            },
            "tables": {
                "table1": {
                    "description_html": "Custom <em>table</em> description",
                    "license": "CC BY 3.0 US",
                    "license_url": "https://creativecommons.org/licenses/by/3.0/us/",
                    "columns": {
                        "col1": "Description of column 1",
                        "col2": "Description of column 2",
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
                "table4": {
                    "columns": {
                        "col4": "",
                    },
                },
            },
        },
    },
}


@pytest.mark.anyio
async def test_server_small_metadata_catalog(small_server):
    responses = await small_server.call_tool("get_catalog", {})
    assert len(responses) == 1
    assert json.loads(responses[0].text) == EXPECTED_SMALL_CATALOG


@pytest.mark.anyio
async def test_client_small_metadata_catalog(small_client_session):
    tools = await small_client_session.list_tools()
    assert len(tools.tools) > 0
    result = await small_client_session.call_tool("get_catalog", {})
    assert len(result.content) == 1
    assert len(result.content[0].text) > 0
    assert json.loads(result.content[0].text) == EXPECTED_SMALL_CATALOG
