import json

import pytest


@pytest.mark.anyio
async def test_settings(empty_server):
    # The server should be stateless and return JSON
    assert empty_server.settings.stateless_http
    assert empty_server.settings.json_response


@pytest.mark.anyio
async def test_empty_catalog(empty_server):
    # There should be only one resource that returns the entire catalog of the SQLite connection
    assert [str(resource.uri) for resource in await empty_server.list_resources()] == ["catalog://"]
    assert len(await empty_server.list_resource_templates()) == 0
    resources = await empty_server.read_resource("catalog://")
    assert len(resources) == 1
    assert resources[0].mime_type == "application/json"
    assert json.loads(resources[0].content) == {"databases": {"main": {"tables": {}}}}


@pytest.mark.anyio
async def test_minimal_catalog(minimal_server):
    # There should be only one resource that returns the entire catalog of the SQLite connection
    resources = await minimal_server.read_resource("catalog://")
    assert len(resources) == 1
    assert resources[0].mime_type == "application/json"
    assert json.loads(resources[0].content) == {
        "databases": {
            "main": {
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


@pytest.mark.anyio
async def test_small_metadata_catalog(small_metadata_server):
    # There should be only one resource that returns the entire catalog of the SQLite connection
    resources = await small_metadata_server.read_resource("catalog://")
    assert len(resources) == 1
    assert resources[0].mime_type == "application/json"
    assert json.loads(resources[0].content) == {
        "title": "Index title",
        "license": "ODbL",
        "source_url": "http://example.com/",
        "databases": {
            "main": {
                "source": "Alternative source",
                "source_url": "http://example.com/",
                "queries": {
                    "answer_to_life": "select 42",
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
