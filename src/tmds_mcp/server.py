"""FastMCP server wrapping TmdsClient."""

import uuid
from pathlib import Path

from fastmcp import FastMCP
from pydantic import AwareDatetime, TypeAdapter
from tmdsclient.client.tmdsclient import TmdsClient
from tmdsclient.models.marktlokation import Marktlokation
from tmdsclient.models.messlokation import Messlokation
from tmdsclient.models.netzvertrag import Netzvertrag
from tmdsclient.models.zaehler import Zaehler

_aware_datetime_adapter = TypeAdapter(AwareDatetime)


def create_server(client: TmdsClient) -> FastMCP:
    """Create and return a FastMCP server wired to the given TmdsClient."""
    mcp = FastMCP("tmds-mcp")

    @mcp.tool
    async def get_messlokation(melo_id: str) -> Messlokation | None:
        return await client.get_messlokation(messlokation_id=melo_id)

    @mcp.tool
    async def get_marktlokation(malo_id: str) -> Marktlokation | None:
        return await client.get_marktlokation(malo_id=malo_id)

    @mcp.tool
    async def get_zaehler(zaehler_id: str, keydate: str | None = None) -> Zaehler | None:
        parsed_id = uuid.UUID(zaehler_id)
        parsed_keydate: AwareDatetime | None = None
        if keydate is not None:
            parsed_keydate = _aware_datetime_adapter.validate_python(keydate)
        return await client.get_zaehler(zaehler_id=parsed_id, keydate=parsed_keydate)

    @mcp.tool
    async def get_netzvertraege_for_melo(melo_id: str) -> list[Netzvertrag]:
        return await client.get_netzvertraege_for_melo(melo_id=melo_id)

    @mcp.tool
    async def get_netzvertraege_for_malo(malo_id: str) -> list[Netzvertrag]:
        return await client.get_netzvertraege_for_malo(malo_id=malo_id)

    @mcp.tool
    async def get_netzvertrag_by_id(nv_id: str) -> Netzvertrag | None:
        parsed_id = uuid.UUID(nv_id)
        return await client.get_netzvertrag_by_id(nv_id=parsed_id)

    @mcp.prompt
    def bug_hunt_workflow() -> str:
        """TMDS bug hunt workflow — which tool to use when and in which order."""
        return (Path(__file__).parent / "DEBUGGING.md").read_text(encoding="utf-8")

    return mcp


def main() -> None:  # pragma: no cover
    """Entry point: read env-var settings, build the client, and run the MCP server."""
    from tmds_mcp.settings import TmdsMcpSettings  # pylint: disable=import-outside-toplevel

    settings = TmdsMcpSettings()  # type: ignore[call-arg]  # pydantic-settings reads TMDS_URL from env

    client = settings.create_client()
    mcp = create_server(client)
    mcp.run()
