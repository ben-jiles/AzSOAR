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


# Placeholder commands (we'll implement these in later tasks)
@app.command()
def generate(
    template: str = typer.Argument(..., help="Template name (e.g. phishing-response)"),
    output: Path = typer.Option("./playbooks", "--output", "-o"),
):
    """Generate a new SOAR playbook from template"""
    console.print(f"Generating playbook from template: [bold]{template}[/]")
    # Implementation in Task 4


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


if __name__ == "__main__":
    app()
