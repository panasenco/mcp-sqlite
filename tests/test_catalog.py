import json

import pytest


@pytest.mark.anyio
async def test_empty_catalog(empty_tuple):
    empty_stem, empty_session = empty_tuple
    tools = await empty_session.list_tools()
    assert len(tools.tools) > 0
    result = await empty_session.call_tool("sqlite_get_catalog", {})
    assert len(result.content) == 1
    assert len(result.content[0].text) > 0
    assert json.loads(result.content[0].text) == {
        "databases": {"main": {"title": empty_stem, "queries": {}, "tables": {}}}
    }


@pytest.mark.anyio
async def test_minimal_catalog(minimal_tuple):
    minimal_stem, minimal_session = minimal_tuple
    # There should be only one resource that returns the entire catalog of the SQLite connection
    result = await minimal_session.call_tool("sqlite_get_catalog", {})
    assert len(result.content) == 1
    assert json.loads(result.content[0].text) == {
        "databases": {
            "main": {
                "title": minimal_stem,
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


@pytest.mark.anyio
async def test_small_metadata_catalog(small_tuple):
    small_stem, small_session = small_tuple
    tools = await small_session.list_tools()
    assert len(tools.tools) > 0
    result = await small_session.call_tool("sqlite_get_catalog", {})
    assert len(result.content) == 1
    assert len(result.content[0].text) > 0
    assert json.loads(result.content[0].text) == {
        "title": "Index title",
        "license": "ODbL",
        "source_url": "http://example.com/",
        "databases": {
            "main": {
                "title": small_stem,
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
