import typer
from pathlib import Path
from src.generator import JournalGenerator

app = typer.Typer()

@app.command()
def generate(
    profile: str = typer.Option("default_a4", help="Printer profile to use (defined in config/printer_profiles.yaml)"),
    start_year: int = typer.Option(None, help="Override start year"),
    output: str = typer.Option("output", help="Output directory")
):
    """
    Generate the Forever Journal PDF.
    """
    try:
        gen = JournalGenerator(profile_name=profile)
        if start_year:
            gen.user_data.start_year = start_year
        
        gen.generate(output_path=output)
        
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def verify_config():
    """Load and validate configuration files without generating PDF."""
    from src.utils import load_user_data, load_printer_profiles
    try:
        u = load_user_data()
        p = load_printer_profiles()
        typer.echo("✅ Configuration valid!")
        typer.echo(f"Found {len(u.special_days.birthdays)} birthdays.")
        typer.echo(f"Found {len(p.profiles)} printer profiles.")
    except Exception as e:
        typer.echo(f"❌ Configuration invalid: {e}")

if __name__ == "__main__":
    app()
