from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from azure.identity import DefaultAzureCredential
import requests
from msgraph_sdk import GraphServiceClient

console = Console()

class IncidentEnricher:
    """Enrich Sentinel incidents with additional context"""
    
    def __init__(self, config=None):
        self.config = config
        self.credential = None
        self.graph_client = None

    async def initialize(self):
        """Initialize authentication"""
        if not self.credential:
            self.credential = DefaultAzureCredential()
        
        if not self.graph_client:
            self.graph_client = GraphServiceClient(
                credentials=self.credential,
                scopes=["https://graph.microsoft.com/.default"]
            )

    async def enrich_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Main enrichment function"""
        await self.initialize()
        
        enriched = incident.copy()
        enriched["enrichment"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "enriched_by": "AzSOAR"
        }

        # 1. User Enrichment (if user info exists)
        if user_principal := self._get_user_principal(incident):
            enriched["enrichment"]["user"] = await self._enrich_user(user_principal)

        # 2. Device Enrichment (if device info exists)
        if device_id := self._get_device_id(incident):
            enriched["enrichment"]["device"] = await self._enrich_device(device_id)

        # 3. Threat Intelligence (basic)
        if ip := self._get_ip_address(incident):
            enriched["enrichment"]["threat_intel"] = self._basic_threat_check(ip)

        console.print("[green]✅ Incident enriched successfully[/]")
        return enriched

    def _get_user_principal(self, incident: Dict) -> Optional[str]:
        """Extract user principal name from incident"""
        # Common paths in Sentinel incidents
        try:
            entities = incident.get("properties", {}).get("additionalData", {}).get("entities", [])
            for entity in entities:
                if entity.get("type") == "account":
                    return entity.get("userPrincipalName") or entity.get("name")
        except:
            pass
        return None

    def _get_device_id(self, incident: Dict) -> Optional[str]:
        """Extract device ID"""
        # TODO: Expand based on real incident format
        return incident.get("properties", {}).get("deviceId")

    def _get_ip_address(self, incident: Dict) -> Optional[str]:
        """Extract IP address"""
        # TODO: Expand
        return None

    async def _enrich_user(self, user_principal: str) -> Dict:
        """Enrich user with Microsoft Graph data"""
        try:
            # Example: Get user risk + sign-in history
            user = await self.graph_client.users.by_user_id(user_principal).get()
            risk = await self.graph_client.security.riskDetections.by_risk_detection_id(user_principal).get()  # Simplified
            
            return {
                "displayName": user.display_name if user else None,
                "riskLevel": getattr(user, "risk_level", "unknown"),
                "accountEnabled": getattr(user, "account_enabled", True),
                "lastSignIn": getattr(user, "last_sign_in_date_time", None)
            }
        except Exception as e:
            console.print(f"[yellow]Warning: User enrichment failed: {e}[/]")
            return {"error": str(e)}

    async def _enrich_device(self, device_id: str) -> Dict:
        """Enrich device info"""
        return {
            "deviceId": device_id,
            "status": "unknown",
            "note": "Expand with Defender for Endpoint API in future"
        }

    def _basic_threat_check(self, ip: str) -> Dict:
        """Basic threat intel placeholder"""
        return {
            "ip": ip,
            "reputation": "unknown",
            "note": "Integrate with VirusTotal / MISP later"
        }
