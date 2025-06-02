import pytest


@pytest.mark.anyio
async def test_server_execute_tool_hello_world(empty_server):
    """Expecting tabular data in HTML format as it performs best according to Siu et al
    https://arxiv.org/pdf/2305.13062
    """
    results = await empty_server.call_tool("execute", {"sql": "select 'hello <world>' as s"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>s</th></tr><tr><td>hello &lt;world&gt;</td></tr></table>"


@pytest.mark.anyio
async def test_server_execute_tool_non_string(empty_server):
    results = await empty_server.call_tool("execute", {"sql": "select 42 as i"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>i</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_server_execute_tool_no_column_name(empty_server):
    results = await empty_server.call_tool("execute", {"sql": "select 42"})
    assert len(results) == 1
    assert results[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_client_execute_tool(small_client_session):
    tools = await small_client_session.list_tools()
    assert len(tools.tools) > 0
    result = await small_client_session.call_tool("execute", {"sql": "select 'hello <world>' as s"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>s</th></tr><tr><td>hello &lt;world&gt;</td></tr></table>"
    result = await small_client_session.call_tool("execute", {"sql": "select 42 as i"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>i</th></tr><tr><td>42</td></tr></table>"
    result = await small_client_session.call_tool("execute", {"sql": "select 42"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"
    result = await small_client_session.call_tool("execute", {"sql": "select * from table1"})
    assert len(result.content) == 1
    assert (
        result.content[0].text
        == """
        <table>
            <tr>
                <th>col1</th>
                <th>col2</th>
            </tr>
            <tr>
                <td>3</td>
                <td>x</td>
            </tr>
            <tr>
                <td>4</td>
                <td>y</td>
            </tr>
        </table>
        """.replace(" ", "").replace("\n", "")
    )


@pytest.mark.anyio
async def test_simple_canned_query(canned_queries_client_session):
    tools = await canned_queries_client_session.list_tools()
    assert len(tools.tools) > 1
    assert "execute_main_answer_to_life" in tools.tools
    result = await canned_queries_client_session.call_tool("execute_main_answer_to_life", {})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"
