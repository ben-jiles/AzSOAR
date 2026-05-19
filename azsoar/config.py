import os
from pathlib import Path
from typing import Optional, Dict
import yaml
from pydantic import BaseModel, Field, field_validator
from azure.identity import (
    DefaultAzureCredential,
    ClientSecretCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
)
from rich.console import Console

console = Console()

class AzSOARConfig(BaseModel):
    """Main configuration model for AzSOAR"""
    
    tenant_id: Optional[str] = Field(None, description="Azure Tenant ID")
    subscription_id: Optional[str] = Field(None, description="Azure Subscription ID")
    workspace_id: Optional[str] = Field(None, description="Log Analytics / Sentinel Workspace ID")
    resource_group: Optional[str] = Field(None, description="Default Resource Group for Logic Apps")
    
    # Authentication preferences
    auth_method: str = Field("default", description="default, cli, managed, sp")
    client_id: Optional[str] = None
    client_secret: Optional[str] = None  # Will never be saved in plain text

    # Paths
    config_dir: Path = Field(default=Path.home() / ".azsoar")
    default_profile: str = "default"

    model_config = {
        "extra": "forbid",  # Prevent unknown fields
    }

    @field_validator("auth_method")
    @classmethod
    def validate_auth_method(cls, v: str) -> str:
        valid = {"default", "cli", "managed", "sp"}
        if v not in valid:
            raise ValueError(f"auth_method must be one of: {valid}")
        return v

    @classmethod
    def get_config_path(cls, profile: str = "default") -> Path:
        return Path.home() / ".azsoar" / f"{profile}.yaml"

    @classmethod
    def load(cls, profile: str = "default") -> "AzSOARConfig":
        """Load config from file or environment variables"""
        config_path = cls.get_config_path(profile)
        
        data: Dict = {}

        # 1. Load from YAML file
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read config file: {e}[/]")

        # 2. Override with Environment Variables (higher priority)
        env_map = {
            "AZSOAR_TENANT_ID": "tenant_id",
            "AZSOAR_SUBSCRIPTION_ID": "subscription_id",
            "AZSOAR_WORKSPACE_ID": "workspace_id",
            "AZSOAR_RESOURCE_GROUP": "resource_group",
            "AZSOAR_AUTH_METHOD": "auth_method",
            "AZSOAR_CLIENT_ID": "client_id",
        }
        
        for env_var, key in env_map.items():
            if os.getenv(env_var):
                data[key] = os.getenv(env_var)

        return cls(**data)

    def save(self, profile: str = "default"):
        """Save config to YAML (never save client_secret)"""
        config_path = self.get_config_path(profile)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(exclude_none=True, exclude={"client_secret", "config_dir"})
        
        with open(config_path, "w") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)
        
        console.print(f"[green]✅ Configuration saved for profile '{profile}'[/]")

    def get_credential(self):
        """Return the appropriate Azure credential with better error messages"""
        try:
            if self.auth_method == "cli":
                console.print("[yellow]Using Azure CLI authentication...[/]")
                return AzureCliCredential()
            elif self.auth_method == "managed":
                console.print("[yellow]Using Managed Identity...[/]")
                return ManagedIdentityCredential()
            elif self.auth_method == "sp":
                if not (self.client_id and self.client_secret and self.tenant_id):
                    raise ValueError("Service Principal requires client_id, client_secret, and tenant_id")
                console.print("[yellow]Using Service Principal authentication...[/]")
                return ClientSecretCredential(...)
            else:
                console.print("[yellow]Using DefaultAzureCredential (recommended)...[/]")
                return DefaultAzureCredential()
        except Exception as e:
            console.print(f"[red]❌ Authentication failed:[/] {e}")
            if "Azure CLI not found" in str(e):
                console.print("[yellow]💡 Tip: Install Azure CLI or switch to --auth default[/]")
            raise
