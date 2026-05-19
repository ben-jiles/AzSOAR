import typer
from rich.console import Console

app = typer.Typer(
    name="azsoar",
    help="AzSOAR - Azure Sentinel SOAR Framework",
    rich_markup_mode="rich"
)

console = Console()

@app.callback()
def callback():
    """AzSOAR CLI"""
    console.print("[bold cyan]🚀 AzSOAR - Azure Sentinel SOAR Framework[/]")

if __name__ == "__main__":
    app()
