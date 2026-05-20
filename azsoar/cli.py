import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from .config import AzSOARConfig

app = typer.Typer(
    name="azsoar",
    help="🚀 AzSOAR - Azure Sentinel SOAR Framework",
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)

console = Console()

@app.callback()
def main_callback(ctx: typer.Context):
    """AzSOAR - Build, test, and run Sentinel SOAR playbooks"""
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "[bold cyan]AzSOAR[/] - Azure Sentinel SOAR Framework\n"
                "[dim]Generate • Test • Deploy • Orchestrate[/]",
                title="Welcome",
                border_style="cyan",
            )
        )
        typer.echo("\nUse [bold]--help[/] for available commands.")


@app.command()
def version():
    """Show AzSOAR version"""
    from . import __version__
    console.print(f"[bold]AzSOAR version:[/] {__version__}")


@app.command()
def config(
    tenant: str = typer.Option(None, "--tenant", help="Azure Tenant ID"),
    subscription: str = typer.Option(None, "--subscription", help="Subscription ID"),
    workspace: str = typer.Option(None, "--workspace", help="Sentinel Workspace ID"),
    resource_group: str = typer.Option(None, "--rg", help="Default Resource Group"),
    auth: str = typer.Option(None, "--auth", help="Auth method: default, cli, managed, sp"),
    profile: str = typer.Option("default", "--profile", "-p"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
):
    """View or update AzSOAR configuration"""
    cfg = AzSOARConfig.load(profile)

    if show:
        console.print(cfg.model_dump_json(indent=2))
        return

    updated = False
    if tenant:
        cfg.tenant_id = tenant
        updated = True
    if subscription:
        cfg.subscription_id = subscription
        updated = True
    if workspace:
        cfg.workspace_id = workspace
        updated = True
    if resource_group:
        cfg.resource_group = resource_group
        updated = True
    if auth:
        cfg.auth_method = auth
        updated = True

    if updated:
        cfg.save(profile)
    else:
        console.print(f"[cyan]Current configuration (profile: {profile}):[/]")
        console.print(cfg.model_dump_json(indent=2))


@app.command()
def login():
    """Test Azure login with DefaultAzureCredential"""
    try:
        cfg = AzSOARConfig.load()
        credential = cfg.get_credential()
        token = credential.get_token("https://management.azure.com/.default")
        console.print("[green]✅ Successfully authenticated to Azure![/]")
        console.print(f"Token expires in ~{token.expires_on}")
    except Exception as e:
        console.print(f"[red]❌ Authentication failed:[/] {e}")


@app.command()
def generate(
    template: str = typer.Argument(..., help="Template name (phishing-response, identity-compromise, ransomware)"),
    output: Path = typer.Option("./playbooks", "--output", "-o", help="Output directory"),
    name: str = typer.Option(None, "--name", help="Custom playbook name"),
    profile: str = typer.Option("default", "--profile", "-p"),
):
    """Generate a new SOAR playbook from template"""
    from .generator import PlaybookGenerator
    
    console.print(f"[bold cyan]Generating playbook:[/] [bold]{template}[/]")
    
    cfg = AzSOARConfig.load(profile)
    generator = PlaybookGenerator(cfg)
    
    try:
        playbook_path = generator.generate(template, output, name)
        console.print(f"[green]✅ Successfully generated playbook at:[/] {playbook_path}")
        console.print(f"[yellow]Next step:[/] Deploy with: az deployment group create ...")
    except Exception as e:
        console.print(f"[red]❌ Generation failed:[/] {e}")


@app.command()
def test(
    playbook: Path = typer.Argument(..., help="Path to playbook file"),
    incident: Path = typer.Option(None, "--incident", help="Mock incident JSON"),
):
    """Test a playbook locally with simulated incident"""
    console.print(f"Testing playbook: [bold]{playbook}[/]")


@app.command()
def run(
    playbook: Path = typer.Argument(..., help="Path to playbook"),
    incident_id: str = typer.Option(None, "--incident-id"),
):
    """Run a playbook against a real Sentinel incident"""
    console.print(f"Running playbook: [bold]{playbook}[/]")

@app.command()
def enrich(
    incident_file: Path = typer.Argument(..., help="Path to incident JSON file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output enriched JSON file"),
    profile: str = typer.Option("default", "--profile", "-p"),
):
    """Enrich a Sentinel incident with additional context"""
    import asyncio
    import json
    from .enrich.enricher import IncidentEnricher
    
    console.print(f"[bold cyan]Enriching incident:[/] {incident_file}")
    
    cfg = AzSOARConfig.load(profile)
    enricher = IncidentEnricher(cfg)
    
    try:
        with open(incident_file) as f:
            incident = json.load(f)
        
        # Run the async enricher
        enriched = asyncio.run(enricher.enrich_incident(incident))
        
        if output:
            output_path = Path(output)
            output_path.write_text(json.dumps(enriched, indent=2))
            console.print(f"[green]✅ Enriched incident saved to:[/] {output_path}")
        else:
            console.print_json(data=enriched)
            
    except Exception as e:
        console.print(f"[red]❌ Enrichment failed:[/] {e}")

@app.command()
def action(
    name: str = typer.Argument(..., help="Action name (isolate-vm, revoke-sessions, force-password-reset, block-ip, disable-user)"),
    user: str = typer.Option(None, "--user", help="User Principal Name"),
    vm: str = typer.Option(None, "--vm", help="VM Name"),
    rg: str = typer.Option(None, "--rg", help="Resource Group"),
    ip: str = typer.Option(None, "--ip", help="IP Address to block"),
    profile: str = typer.Option("default", "--profile", "-p"),
):
    """Execute a single response action"""
    import asyncio
    from .actions.actions import ResponseActions
    
    console.print(f"[bold cyan]Executing action:[/] {name}")
    
    cfg = AzSOARConfig.load(profile)
    actions_obj = ResponseActions(cfg)
    
    try:
        # Keep original kebab-case for consistency with dictionary keys
        result = asyncio.run(
            actions_obj.execute(name, resource_group=rg, vm_name=vm, user_principal=user, ip_address=ip)
        )
        console.print_json(data=result)
        
    except Exception as e:
        console.print(f"[red]❌ Action failed:[/] {e}")

@app.command()
def test(
    playbook: Path = typer.Argument(..., help="Path to playbook directory"),
    scenario: str = typer.Option("phishing", "--scenario", "-s", help="phishing, identity, ransomware"),
    output: Path = typer.Option(None, "--output", "-o"),
    profile: str = typer.Option("default", "--profile", "-p"),
):
    """Test a playbook locally with simulated incident"""
    from .test.simulator import SentinelSimulator
    import json
    
    console.print(f"[bold cyan]Running local test for:[/] {playbook}")
    
    simulator = SentinelSimulator()
    mock_incident = simulator.create_mock_incident(scenario)
    
    # Save mock for future use
    mock_path = simulator.save_mock(mock_incident)
    
    result = simulator.run_simulation(playbook, mock_incident)
    
    if output:
        output.write_text(json.dumps(result, indent=2))
        console.print(f"[green]✅ Test report saved to:[/] {output}")
    else:
        console.print_json(data=result)

@app.command()
def history(limit: int = typer.Option(20, "--limit", "-n")):
    """Show recent playbook/action execution history"""
    from .monitoring.logger import execution_logger
    logs = execution_logger.get_execution_history(limit)
    
    console.print(f"[bold cyan]Last {len(logs)} executions:[/]")
    for log in logs[-10:]:  # Show last 10
        color = "green" if log["status"] == "success" else "red"
        console.print(f"[{color}]{log['timestamp'][:19]}[/] | {log['action']} | {log['playbook']}")


@app.command()
def analytics():
    """Show SOAR execution analytics"""
    from .monitoring.logger import execution_logger
    stats = execution_logger.get_analytics()
    
    console.print(Panel.fit(
        f"Total Executions : [bold]{stats['total_executions']}[/]\n"
        f"Success Rate     : [bold green]{stats['success_rate']}%[/]\n"
        f"Last 7 Days      : [bold]{stats['last_7_days']}[/]",
        title="AzSOAR Analytics",
        border_style="cyan"
    ))

@app.command()
def dashboard():
    """Launch the AzSOAR Web Dashboard"""
    import subprocess
    console.print("[bold cyan]Launching AzSOAR Dashboard...[/]")
    console.print("Open your browser at http://localhost:8501")
    
    subprocess.run(["streamlit", "run", "azsoar/dashboard.py"])


if __name__ == "__main__":
    app()
