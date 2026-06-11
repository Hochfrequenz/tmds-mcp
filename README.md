# tmds-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/tmds-mcp.svg)
![Pypi status badge](https://img.shields.io/pypi/v/tmds-mcp)
![Unittests status badge](https://github.com/Hochfrequenz/tmds-mcp/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/tmds-mcp/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/tmds-mcp/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/tmds-mcp/workflows/Formatting/badge.svg)

An [MCP](https://modelcontextprotocol.io/) server wrapping [`tmdsclient`](https://github.com/Hochfrequenz/tmdsclient.py), exposing read-only TMDS master data to AI assistants (e.g. Claude Desktop) for debugging.

Requires **Python 3.11+**.

## Tools

| Tool | Description |
|---|---|
| `get_messlokation` | Messlokation (meter location) master data by MeLo-ID |
| `get_marktlokation` | Marktlokation (market location) master data by MaLo-ID |
| `get_zaehler` | Zähler (meter) data by UUID, optionally at a historical keydate |
| `get_netzvertraege_for_melo` | All Netzverträge for a MeLo-ID |
| `get_netzvertraege_for_malo` | All Netzverträge for a MaLo-ID |
| `get_netzvertrag_by_id` | Single Netzvertrag by UUID |

## Installation

```bash
pip install tmds-mcp
```

For use with [Claude Desktop](https://claude.ai/download) or another MCP client, `pipx` installs the server as a standalone executable:

```bash
pipx install tmds-mcp
```

## Configuration

Set environment variables or place them in a `.env` file in the working directory from which the MCP server is launched:

| Variable | Required | Description |
|---|---|---|
| `TMDS_URL` | Yes | Base URL of the TMDS server, e.g. `https://techmasterdata.example.de/` |
| `TMDS_AUTH_TYPE` | No (default: `basic`) | `basic` or `oauth` |
| `TMDS_USER` | If basic auth | Username |
| `TMDS_PASSWORD` | If basic auth | Password |
| `TMDS_CLIENT_ID` | If OAuth | OAuth client ID |
| `TMDS_CLIENT_SECRET` | If OAuth | OAuth client secret |
| `TMDS_TOKEN_URL` | If OAuth | Token endpoint URL |

## Usage

Run the server directly:

```bash
tmds-mcp
```

Or add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "tmds": {
      "command": "tmds-mcp",
      "env": {
        "TMDS_URL": "https://techmasterdata.example.de/",
        "TMDS_AUTH_TYPE": "basic",
        "TMDS_USER": "...",
        "TMDS_PASSWORD": "..."
      }
    }
  }
}
```

## Development

This project follows the [Hochfrequenz Python template](https://github.com/Hochfrequenz/python_template_repository):

```bash
tox -e tests       # run tests
tox -e type_check  # mypy --strict
tox -e linting     # pylint
tox -e coverage    # coverage ≥ 80 %
tox -e formatting  # black + isort
```
