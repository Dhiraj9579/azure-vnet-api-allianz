"""Application settings for the Azure VNet challenge."""
import os


class Settings:
    def __init__(self):
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
        self.JWT_ALGORITHM: str = "HS256"
        self.JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vnet-api.db")

        self.AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        self.AZURE_RESOURCE_GROUP: str = os.getenv("AZURE_RESOURCE_GROUP", "vnet-resource-group")
        self.AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
        self.AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
        self.AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")

        self.CORS_ORIGINS: list = ["*"]
        self.CORS_CREDENTIALS: bool = True
        self.CORS_METHODS: list = ["*"]
        self.CORS_HEADERS: list = ["*"]

        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
