"""Configuration management using pydantic-settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration (Azure OpenAI)
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-05-01-preview"
    azure_openai_deployment: str

    # Jenkins MCP Configuration
    jenkins_mcp_url: str
    jenkins_mcp_token: str

    # Agent Configuration
    agent_name: str = "Jenkins AI Agent"
    log_level: str = "INFO"


# Global settings instance
settings = Settings()
