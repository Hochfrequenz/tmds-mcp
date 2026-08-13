# tmds-mcp

MCP server wrapping the `tmdsclient` library for read-only TMDS (Technical Master Data Service) debug tooling.

## Core principle: typed all the way down

MCP tool signatures mirror the underlying `TmdsClient` methods exactly — same parameter types, same Pydantic return types. No `dict`, no `Any`, no raw JSON in tool interfaces. If `tmdsclient` returns `Messlokation | None`, the tool returns `Messlokation | None`. FastMCP uses the type annotations to generate the tool schema and to populate `result.data` on the client side — a missing or `Any` annotation breaks schema generation silently.

## Server structure

- `src/tmds_mcp/server.py` — `create_server(client: TmdsClient) -> FastMCP` factory (pure, no I/O) + `main()` entry point
- `src/tmds_mcp/settings.py` — pydantic-settings reading env vars, building `BasicAuthTmdsClient` or `OAuthTmdsClient`

`create_server` is the seam for tests: tests call it with `AsyncMock(spec=TmdsClient)`, production calls it with the real client.

## Testing

Tests use the official FastMCP in-process pattern:

```python
async with Client(create_server(mock_client)) as client:
    result = await client.call_tool("tool_name", {...})
```

Mock strategy: `AsyncMock(spec=TmdsClient)` — never a Protocol, never a concrete subclass.

Every test asserts both `result.data` and `mock.method.assert_awaited_once_with(...)` with explicit arguments. A tool that forgets to forward a parameter must not silently pass.

Tool exceptions propagate as `fastmcp.exceptions.ToolError` on the client side — use `pytest.raises(ToolError, match=...)` in error-path tests.

## Read-only scope

The server only exposes read-only `TmdsClient` methods. Write operations (`update_*`, `set_*`) are excluded permanently.

## CI

Set `PYTHONPATH=src` (src layout) for the commands that need it — matches CI:

```
# pytest
PYTHONPATH=src uv run --group tests pytest
# mypy --strict (src + unittests)
PYTHONPATH=src uv run --group type_check mypy --show-error-codes src/tmds_mcp --strict
PYTHONPATH=src uv run --group type_check mypy --show-error-codes unittests --strict
# ruff (lint)
PYTHONPATH=src uv run --group linting ruff check .
# coverage ≥ 80%
PYTHONPATH=src uv run --group coverage coverage run -m pytest
PYTHONPATH=src uv run --group coverage coverage report --fail-under 80 --omit "unittests/*"
# ruff (format)
uv run --group linting ruff format --check .
```
