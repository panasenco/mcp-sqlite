import pytest


@pytest.mark.anyio
async def test_canned_query_answer_to_life(canned_tuple):
    _, canned_session = canned_tuple
    tools = await canned_session.list_tools()
    assert len(tools.tools) > 1
    assert "sqlite_execute_main_answer_to_life" in [tool.name for tool in tools.tools]
    result = await canned_session.call_tool("sqlite_execute_main_answer_to_life", {})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_canned_query_add_integers(canned_tuple):
    _, canned_session = canned_tuple
    result = await canned_session.call_tool("sqlite_execute_main_add_integers", {"a": 3, "b": 9})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>total</th></tr><tr><td>12</td></tr></table>"


@pytest.mark.anyio
async def test_canned_query_write_fails(canned_tuple):
    _, canned_session = canned_tuple
    result = await canned_session.call_tool("sqlite_execute_main_write_fails", {"value": 8})
    assert len(result.content) == 1
    assert result.content[0].text == "attempt to write a readonly database"


@pytest.mark.anyio
async def test_canned_query_write_succeeds(canned_tuple):
    _, canned_session = canned_tuple
    result = await canned_session.call_tool("sqlite_execute_main_write_succeeds", {"value": 8})
    assert len(result.content) == 1
    assert result.content[0].text == "Statement executed successfully"
