import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
import yaml

console = Console()

class SentinelSimulator:
    """Local testing framework for Sentinel playbooks"""
    
    def __init__(self):
        self.incidents = {}
        self.test_data_dir = Path("samples/test_data")
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def create_mock_incident(self, scenario: str = "phishing") -> Dict:
        """Create realistic mock incidents"""
        templates = {
            "phishing": {
                "id": f"inc-{datetime.now().strftime('%Y%m%d%H%M')}",
                "properties": {
                    "title": "Potential Phishing Email Reported",
                    "severity": "Medium",
                    "status": "New",
                    "incidentNumber": 12345,
                    "additionalData": {
                        "entities": [
                            {
                                "type": "account",
                                "userPrincipalName": "user@yourdomain.com",
                                "name": "John Doe"
                            },
                            {
                                "type": "ip",
                                "address": "203.0.113.42"
                            }
                        ]
                    }
                }
            },
            "identity": {
                "id": f"inc-{datetime.now().strftime('%Y%m%d%H%M')}",
                "properties": {
                    "title": "Impossible Travel Detected",
                    "severity": "High",
                    "additionalData": {
                        "entities": [{"type": "account", "userPrincipalName": "admin@yourdomain.com"}]
                    }
                }
            },
            "ransomware": {
                "id": f"inc-{datetime.now().strftime('%Y%m%d%H%M')}",
                "properties": {
                    "title": "Ransomware Activity Detected",
                    "severity": "Critical",
                    "additionalData": {
                        "entities": [{"type": "host", "hostName": "prod-server-01"}]
                    }
                }
            }
        }
        return templates.get(scenario, templates["phishing"])

    def save_mock(self, incident: Dict, filename: str = None):
        """Save mock incident for reuse"""
        if not filename:
            filename = f"mock-{incident['id']}.json"
        
        path = self.test_data_dir / filename
        with open(path, "w") as f:
            json.dump(incident, f, indent=2)
        console.print(f"[green]✅ Mock incident saved:[/] {path}")
        return path

    def run_simulation(self, playbook_path: Path, incident: Dict) -> Dict:
        """Simulate running a playbook locally"""
        console.print(f"[bold cyan]Simulating playbook:[/] {playbook_path.name}")
        
        result = {
            "simulation_id": f"sim-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "playbook": playbook_path.name,
            "incident_id": incident.get("id"),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "actions_taken": [],
            "enrichment": {},
            "recommendations": []
        }

        # Simulate common actions based on incident title
        title = incident.get("properties", {}).get("title", "").lower()
        
        if "phishing" in title:
            result["actions_taken"] = ["revoke_sessions", "force_password_reset"]
            result["recommendations"] = ["Review email headers", "Block sender domain"]
        elif "impossible travel" in title or "identity" in title:
            result["actions_taken"] = ["revoke_sessions", "disable_user"]
        elif "ransomware" in title:
            result["actions_taken"] = ["isolate_vm", "block_ip"]

        console.print(f"[green]✅ Simulation completed with {len(result['actions_taken'])} actions[/]")
        return result
