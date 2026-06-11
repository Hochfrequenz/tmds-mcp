"""Tests for tmds_mcp.server."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError

from unittests.conftest import (
    build_marktlokation,
    build_messlokation,
    build_netzvertrag,
    build_zaehler,
)


async def test_server_exposes_expected_tools(tmds_server: FastMCP) -> None:
    async with Client(tmds_server) as client:
        tools = await client.list_tools()
    assert {t.name for t in tools} == {
        "get_messlokation",
        "get_marktlokation",
        "get_zaehler",
        "get_netzvertraege_for_melo",
        "get_netzvertraege_for_malo",
        "get_netzvertrag_by_id",
    }


async def test_get_messlokation_returns_result(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    melo = build_messlokation()
    mock_tmds_client.get_messlokation.return_value = melo
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_messlokation", {"melo_id": "DE000122110001"})
    assert result.data is not None
    mock_tmds_client.get_messlokation.assert_awaited_once_with(messlokation_id="DE000122110001")


async def test_get_messlokation_returns_none(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_messlokation.return_value = None
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_messlokation", {"melo_id": "DE000122110001"})
    assert result.data is None


async def test_get_messlokation_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_messlokation.side_effect = Exception("TMDS unavailable")
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="TMDS unavailable"):
            await client.call_tool("get_messlokation", {"melo_id": "DE000122110001"})


async def test_get_marktlokation_returns_result(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    malo = build_marktlokation()
    mock_tmds_client.get_marktlokation.return_value = malo
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_marktlokation", {"malo_id": "51238696781"})
    assert result.data is not None
    mock_tmds_client.get_marktlokation.assert_awaited_once_with(malo_id="51238696781")


async def test_get_marktlokation_returns_none(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_marktlokation.return_value = None
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_marktlokation", {"malo_id": "51238696781"})
    assert result.data is None


async def test_get_marktlokation_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_marktlokation.side_effect = Exception("not found")
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="not found"):
            await client.call_tool("get_marktlokation", {"malo_id": "51238696781"})


async def test_get_zaehler_returns_result(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    zaehler = build_zaehler()
    zaehler_uuid = zaehler.id
    mock_tmds_client.get_zaehler.return_value = zaehler
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_zaehler", {"zaehler_id": str(zaehler_uuid)})
    assert result.data is not None
    mock_tmds_client.get_zaehler.assert_awaited_once_with(zaehler_id=zaehler_uuid, keydate=None)


async def test_get_zaehler_with_keydate(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    zaehler = build_zaehler()
    zaehler_uuid = zaehler.id
    mock_tmds_client.get_zaehler.return_value = zaehler
    keydate_str = "2024-01-15T10:00:00+00:00"
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_zaehler", {"zaehler_id": str(zaehler_uuid), "keydate": keydate_str})
    assert result.data is not None
    call_kwargs = mock_tmds_client.get_zaehler.call_args
    assert call_kwargs.kwargs["zaehler_id"] == zaehler_uuid
    assert call_kwargs.kwargs["keydate"] == datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)


async def test_get_zaehler_returns_none(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_zaehler.return_value = None
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_zaehler", {"zaehler_id": str(uuid.uuid4())})
    assert result.data is None


async def test_get_zaehler_rejects_invalid_uuid(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_zaehler", {"zaehler_id": "not-a-uuid"})
    mock_tmds_client.get_zaehler.assert_not_awaited()


async def test_get_zaehler_rejects_naive_datetime(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_zaehler", {"zaehler_id": str(uuid.uuid4()), "keydate": "2024-01-15T10:00:00"})
    mock_tmds_client.get_zaehler.assert_not_awaited()


async def test_get_zaehler_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_zaehler.side_effect = Exception("zaehler unavailable")
    zaehler_id = str(uuid.uuid4())
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="zaehler unavailable"):
            await client.call_tool("get_zaehler", {"zaehler_id": zaehler_id})


async def test_get_netzvertraege_for_melo_returns_list(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    nv = build_netzvertrag()
    mock_tmds_client.get_netzvertraege_for_melo.return_value = [nv]
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_netzvertraege_for_melo", {"melo_id": "DE000122110001"})
    assert result.data is not None
    assert len(result.data) == 1
    mock_tmds_client.get_netzvertraege_for_melo.assert_awaited_once_with(melo_id="DE000122110001")


async def test_get_netzvertraege_for_melo_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_netzvertraege_for_melo.side_effect = Exception("melo error")
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="melo error"):
            await client.call_tool("get_netzvertraege_for_melo", {"melo_id": "DE000122110001"})


async def test_get_netzvertraege_for_malo_returns_list(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    nv = build_netzvertrag()
    mock_tmds_client.get_netzvertraege_for_malo.return_value = [nv]
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_netzvertraege_for_malo", {"malo_id": "51238696781"})
    assert result.data is not None
    assert len(result.data) == 1
    mock_tmds_client.get_netzvertraege_for_malo.assert_awaited_once_with(malo_id="51238696781")


async def test_get_netzvertraege_for_malo_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_netzvertraege_for_malo.side_effect = Exception("malo error")
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="malo error"):
            await client.call_tool("get_netzvertraege_for_malo", {"malo_id": "51238696781"})


async def test_get_netzvertrag_by_id_returns_result(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    nv = build_netzvertrag()
    nv_uuid = nv.id
    mock_tmds_client.get_netzvertrag_by_id.return_value = nv
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_netzvertrag_by_id", {"nv_id": str(nv_uuid)})
    assert result.data is not None
    mock_tmds_client.get_netzvertrag_by_id.assert_awaited_once_with(nv_id=nv_uuid)


async def test_get_netzvertrag_by_id_returns_none(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_netzvertrag_by_id.return_value = None
    async with Client(tmds_server) as client:
        result = await client.call_tool("get_netzvertrag_by_id", {"nv_id": str(uuid.uuid4())})
    assert result.data is None


async def test_get_netzvertrag_by_id_rejects_invalid_uuid(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_netzvertrag_by_id", {"nv_id": "not-a-uuid"})
    mock_tmds_client.get_netzvertrag_by_id.assert_not_awaited()


async def test_get_netzvertrag_by_id_propagates_error(tmds_server: FastMCP, mock_tmds_client: AsyncMock) -> None:
    mock_tmds_client.get_netzvertrag_by_id.side_effect = Exception("nv not found")
    nv_id = str(uuid.uuid4())
    async with Client(tmds_server) as client:
        with pytest.raises(ToolError, match="nv not found"):
            await client.call_tool("get_netzvertrag_by_id", {"nv_id": nv_id})
