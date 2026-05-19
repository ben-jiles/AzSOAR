import os
from pathlib import Path
from typing import Optional
import yaml
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel

class AzSOARConfig(BaseModel):
    tenant_id: Optional[str] = None
    subscription_id: Optional[str] = None
    workspace_id: Optional[str] = None  # Sentinel Workspace ID
    resource_group: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AzSOARConfig":
        if config_path is None:
            config_path = Path.home() / ".azsoar" / "config.yaml"

        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)

        return cls()

    def save(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".azsoar" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(exclude_none=True), f)

    def get_credential(self):
        return DefaultAzureCredential(
            tenant_id=self.tenant_id,
        )
