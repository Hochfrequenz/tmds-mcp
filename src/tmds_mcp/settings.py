"""Env-var configuration for tmds-mcp."""

from enum import StrEnum

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from tmdsclient.client.config import BasicAuthTmdsConfig, OAuthTmdsConfig
from tmdsclient.client.tmdsclient import BasicAuthTmdsClient, OAuthTmdsClient, TmdsClient
from yarl import URL


class AuthType(StrEnum):
    """Authentication type supported by the TMDS server."""

    BASIC = "basic"
    OAUTH = "oauth"


class TmdsMcpSettings(BaseSettings):
    """Pydantic-settings model reading TMDS_* environment variables."""

    model_config = SettingsConfigDict(env_prefix="TMDS_", env_file=".env", extra="ignore")

    url: HttpUrl
    auth_type: AuthType = AuthType.BASIC
    user: str = ""
    password: str = ""
    client_id: str = ""
    client_secret: str = ""
    token_url: HttpUrl | None = None

    def create_client(self) -> TmdsClient:
        """Instantiate the appropriate TmdsClient based on the configured auth type."""
        server_url = URL(str(self.url))
        if self.auth_type == AuthType.OAUTH:
            if self.token_url is None:
                raise ValueError("TMDS_TOKEN_URL is required when TMDS_AUTH_TYPE=oauth")
            return OAuthTmdsClient(
                OAuthTmdsConfig(
                    server_url=server_url,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_url=self.token_url,
                )
            )
        return BasicAuthTmdsClient(BasicAuthTmdsConfig(server_url=server_url, usr=self.user, pwd=self.password))
