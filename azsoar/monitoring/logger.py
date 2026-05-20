import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
import yaml

console = Console()

class ExecutionLogger:
    """Central logging and analytics for AzSOAR executions"""
    
    def __init__(self, config=None):
        self.config = config
        self.log_dir = Path.home() / ".azsoar" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_run_id = str(uuid.uuid4())[:8]

    def log_execution(self, 
                     playbook_name: str, 
                     action: str, 
                     status: str, 
                     details: Dict = None,
                     incident_id: str = None) -> str:
        """Log a playbook or action execution"""
        log_entry = {
            "run_id": self.current_run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "playbook": playbook_name,
            "action": action,
            "status": status,
            "incident_id": incident_id,
            "details": details or {},
            "user": "local",  # Can be extended with identity
        }

        # Save to JSON log
        log_file = self.log_dir / f"azsoar-run-{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Rich console output
        color = "green" if status == "success" else "red"
        console.print(f"[{color}]{status.upper()}[/] | {action} | {playbook_name}")

        return self.current_run_id

    def get_execution_history(self, limit: int = 50) -> list:
        """Return recent executions"""
        logs = []
        for log_file in sorted(self.log_dir.glob("*.jsonl"), reverse=True):
            with open(log_file) as f:
                for line in f:
                    logs.append(json.loads(line))
            if len(logs) >= limit:
                break
        return logs[-limit:]

    def get_analytics(self) -> Dict:
        """Basic analytics summary"""
        history = self.get_execution_history(1000)
        
        total = len(history)
        success = sum(1 for x in history if x["status"] == "success")
        
        return {
            "total_executions": total,
            "success_rate": round((success / total * 100), 2) if total > 0 else 0,
            "most_used_actions": {},
            "last_7_days": len([x for x in history if 
                              (datetime.utcnow() - datetime.fromisoformat(x["timestamp"].replace("Z",""))).days <= 7])
        }


# Global logger instance
execution_logger = ExecutionLogger()
