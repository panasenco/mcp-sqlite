from pathlib import Path
import tempfile
import time

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import pytest
import yaml


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


@pytest.mark.anyio
async def test_simple_canned_query(canned_queries_client_session):
    tools = await canned_queries_client_session.list_tools()
    assert len(tools.tools) > 1
    assert "execute_main_answer_to_life" in [tool.name for tool in tools.tools]
    result = await canned_queries_client_session.call_tool("execute_main_answer_to_life", {})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"
