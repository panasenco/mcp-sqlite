import pytest


@pytest.mark.anyio
async def test_execute_hello_world(empty_tuple):
    """Expecting tabular data in HTML format as it performs best according to Siu et al
    https://arxiv.org/pdf/2305.13062
    """
    _, empty_session = empty_tuple
    tools = await empty_session.list_tools()
    assert len(tools.tools) > 0
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 'hello <world>' as s"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>s</th></tr><tr><td>hello &lt;world&gt;</td></tr></table>"


@pytest.mark.anyio
async def test_execute_non_string(empty_tuple):
    _, empty_session = empty_tuple
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 42 as i"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>i</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_execute_no_column_name(empty_tuple):
    _, empty_session = empty_tuple
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 42"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_execute_no_rows(minimal_tuple):
    _, minimal_session = minimal_tuple
    result = await minimal_session.call_tool("sqlite_execute", {"sql": "select * from table1"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>col1</th><th>col2</th></tr></table>"


@pytest.mark.anyio
async def test_execute_table(small_tuple):
    _, small_session = small_tuple
    result = await small_session.call_tool("sqlite_execute", {"sql": "select * from table1"})
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
async def test_execute_write_not_allowed_default(empty_tuple):
    _, empty_session = empty_tuple
    result = await empty_session.call_tool("sqlite_execute", {"sql": "create table tbl1 (col1, col2)"})
    assert result.content[0].text == "attempt to write a readonly database"
