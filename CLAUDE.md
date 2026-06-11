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

```
tox -e tests       # pytest
tox -e type_check  # mypy --strict
tox -e linting     # pylint
tox -e coverage    # coverage ≥ 80%
tox -e formatting  # black + isort
```
