import pytest


@pytest.mark.anyio
async def test_list_resources(mcp_client_session):
    resources = await mcp_client_session.list_resources()
    assert len(resources) == 1
