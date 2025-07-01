import pytest


@pytest.mark.anyio
async def test_default_tools_have_descriptions(empty_tuple):
    _, empty_session = empty_tuple
    tools = await empty_session.list_tools()
    for tool in tools.tools:
        assert tool.description is not None
        assert len(tool.description) >= 80


@pytest.mark.anyio
async def test_canned_query_tools_have_descriptions(small_tuple):
    _, small_session = small_tuple
    tools = await small_session.list_tools()
    for tool in tools.tools:
        assert tool.description is not None
        assert len(tool.description) >= 80
    canned_tool = [tool for tool in tools.tools if tool.name.startswith("sqlite_execute_")][0]
    # The SQL of the canned query should be provided in the description by default
    assert "answer_to_life" in canned_tool.description
    assert "main_answer_to_life" not in canned_tool.description
    assert "select 42" in canned_tool.description


@pytest.mark.anyio
async def test_canned_query_tools_advanced_descriptions(canned_tuple):
    _, canned_session = canned_tuple
    tools = await canned_session.list_tools()
    descriptive_tool = [tool for tool in tools.tools if tool.name == "sqlite_execute_main_descriptive"][0]
    assert "My useful title" in descriptive_tool.description
    assert "My description" in descriptive_tool.description
    assert "this_should_not_appear_in_description" not in descriptive_tool.description
