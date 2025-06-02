import pytest


@pytest.mark.anyio
async def test_execute_tool_hello_world(empty_server):
    """Expecting tabular data in HTML format as it performs best according to Siu et al
    https://arxiv.org/pdf/2305.13062
    """
    results = await empty_server.call_tool("execute", {"sql": "select 'hello <world>' as s"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>s</th></tr><tr><td>hello &lt;world&gt;</td></tr></table>"


@pytest.mark.anyio
async def test_execute_tool_non_string(empty_server):
    results = await empty_server.call_tool("execute", {"sql": "select 42 as i"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>i</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_execute_tool_no_column_name(empty_server):
    results = await empty_server.call_tool("execute", {"sql": "select 42"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"
