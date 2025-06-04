import pytest


@pytest.mark.anyio
async def test_execute_hello_world(empty_session):
    """Expecting tabular data in HTML format as it performs best according to Siu et al
    https://arxiv.org/pdf/2305.13062
    """
    tools = await empty_session.list_tools()
    assert len(tools.tools) > 0
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 'hello <world>' as s"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>s</th></tr><tr><td>hello &lt;world&gt;</td></tr></table>"


@pytest.mark.anyio
async def test_execute_non_string(empty_session):
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 42 as i"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>i</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_execute_no_column_name(empty_session):
    result = await empty_session.call_tool("sqlite_execute", {"sql": "select 42"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>42</th></tr><tr><td>42</td></tr></table>"


@pytest.mark.anyio
async def test_execute_no_rows(minimal_session):
    result = await minimal_session.call_tool("sqlite_execute", {"sql": "select * from table1"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>col1</th><th>col2</th></tr></table>"


@pytest.mark.anyio
async def test_execute_table(small_session):
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
async def test_execute_write_not_allowed_default(empty_session):
    result = await empty_session.call_tool("sqlite_execute", {"sql": "create table tbl1 (col1, col2)"})
    assert result.content[0].text == "attempt to write a readonly database"


@pytest.mark.anyio
async def test_execute_write_works_when_allowed(empty_session_write_allowed):
    result = await empty_session_write_allowed.call_tool("sqlite_execute", {"sql": "create table tbl1 (col1, col2)"})
    assert len(result.content) == 1
    assert result.content[0].text == "Statement executed successfully"
    result = await empty_session_write_allowed.call_tool("sqlite_execute", {"sql": "select * from tbl1"})
    assert len(result.content) == 1
    assert result.content[0].text == "<table><tr><th>col1</th><th>col2</th></tr></table>"
