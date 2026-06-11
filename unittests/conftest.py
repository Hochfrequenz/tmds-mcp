"""Shared fixtures and test-data builders."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastmcp import FastMCP
from tmdsclient.client.tmdsclient import TmdsClient
from tmdsclient.models.marktlokation import Marktlokation
from tmdsclient.models.messlokation import Messlokation
from tmdsclient.models.netzvertrag import Netzvertrag
from tmdsclient.models.zaehler import Zaehler

from tmds_mcp.server import create_server


@pytest.fixture
def mock_tmds_client() -> AsyncMock:
    return AsyncMock(spec=TmdsClient)


@pytest.fixture
def tmds_server(mock_tmds_client: AsyncMock) -> FastMCP:
    return create_server(mock_tmds_client)


def build_messlokation() -> Messlokation:
    melo_id = "DE000122110001"
    return Messlokation.model_validate(
        {
            "id": melo_id,
            "boModel": {
                "_typ": "MESSLOKATION",
                "messlokationsId": melo_id,
            },
        }
    )


def build_marktlokation() -> Marktlokation:
    malo_id = "51238696781"
    return Marktlokation.model_validate(
        {
            "id": malo_id,
            "boModel": {
                "_typ": "MARKTLOKATION",
                "marktlokationsId": malo_id,
            },
        }
    )


def build_netzvertrag() -> Netzvertrag:
    return Netzvertrag.model_validate(
        {
            "id": str(uuid4()),
        }
    )


def build_zaehler() -> Zaehler:
    zaehler_uuid = uuid4()
    return Zaehler.model_validate(
        {
            "id": str(zaehler_uuid),
            "externeId": "Z123456",
            "boModel": {
                "boTyp": "ZAEHLER",
                "versionStruktur": "1",
                "zaehlernummer": "Z123456",
                "sparte": "STROM",
            },
            "sperrzustand": "ENTSPERRT",
        }
    )
