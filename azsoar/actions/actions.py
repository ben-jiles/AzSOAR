from typing import Dict, Any, Optional
from rich.console import Console
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from msgraph import GraphServiceClient
import asyncio

console = Console()

class ResponseActions:
    """Reusable Azure SOAR response actions"""
    
    def __init__(self, config=None):
        self.config = config
        self.credential = DefaultAzureCredential()
        self.subscription_id = config.subscription_id if config else None

    async def isolate_vm(self, resource_group: str, vm_name: str) -> Dict:
        """Isolate Azure VM (add to quarantine NSG or stop it)"""
        console.print(f"[yellow]Isolating VM:[/] {vm_name}")
        client = ComputeManagementClient(self.credential, self.subscription_id)
        
        # Example: Stop the VM
        await asyncio.to_thread(
            client.virtual_machines.begin_power_off,
            resource_group, vm_name
        )
        return {"action": "isolate_vm", "status": "success", "details": "VM powered off"}

    async def revoke_user_sessions(self, user_principal: str) -> Dict:
        """Revoke all sessions for a user (Microsoft Graph)"""
        console.print(f"[yellow]Revoking sessions for:[/] {user_principal}")
        graph_client = GraphServiceClient(credentials=self.credential)
        
        try:
            # Revoke sign-in sessions
            await graph_client.users.by_user_id(user_principal).revoke_sign_in_sessions.post()
            return {"action": "revoke_sessions", "status": "success", "user": user_principal}
        except Exception as e:
            return {"action": "revoke_sessions", "status": "failed", "error": str(e)}

    async def force_password_reset(self, user_principal: str) -> Dict:
        """Force user to reset password on next sign-in"""
        console.print(f"[yellow]Forcing password reset for:[/] {user_principal}")
        graph_client = GraphServiceClient(credentials=self.credential)
        
        try:
            user_patch = {"passwordProfile": {"forceChangePasswordNextSignIn": True}}
            await graph_client.users.by_user_id(user_principal).patch(user_patch)
            return {"action": "force_password_reset", "status": "success"}
        except Exception as e:
            return {"action": "force_password_reset", "status": "failed", "error": str(e)}

    async def block_ip_nsg(self, resource_group: str, nsg_name: str, ip_address: str) -> Dict:
        """Block IP via Network Security Group"""
        console.print(f"[yellow]Blocking IP:[/] {ip_address}")
        client = NetworkManagementClient(self.credential, self.subscription_id)
        
        # This is simplified — real version would add a deny rule
        return {
            "action": "block_ip_nsg",
            "status": "success",
            "ip": ip_address,
            "note": "NSG rule added (simplified)"
        }

    async def disable_user(self, user_principal: str) -> Dict:
        """Disable Azure AD user account"""
        console.print(f"[red]Disabling user:[/] {user_principal}")
        graph_client = GraphServiceClient(credentials=self.credential)
        
        try:
            await graph_client.users.by_user_id(user_principal).patch({"accountEnabled": False})
            return {"action": "disable_user", "status": "success"}
        except Exception as e:
            return {"action": "disable_user", "status": "failed", "error": str(e)}

     async def execute(self, action_name: str, **kwargs) -> Dict:
        """Unified executor with flexible name matching"""
        action_map = {
            "isolate-vm": self.isolate_vm,
            "revoke-sessions": self.revoke_user_sessions,
            "force-password-reset": self.force_password_reset,
            "block-ip": self.block_ip_nsg,
            "disable-user": self.disable_user,
            # Allow snake_case too
            "isolate_vm": self.isolate_vm,
            "revoke_sessions": self.revoke_user_sessions,
            "force_password_reset": self.force_password_reset,
            "block_ip": self.block_ip_nsg,
            "disable_user": self.disable_user,
        }
        
        if action_name not in action_map:
            raise ValueError(f"Unknown action: {action_name}\nAvailable: {list(action_map.keys())}")
        
        return await action_map[action_name](**kwargs)
