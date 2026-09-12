import typer
from pathlib import Path
from datetime import datetime

from airbnb_ops.config import PipelineConfig
from airbnb_ops.extract import read_csv_checked
from airbnb_ops.pii import handle_pii
from airbnb_ops.transform import build_neighbourhood_summary
from airbnb_ops.validate import validate_summary

app = typer.Typer()

@app.command("run")
def run():
    """Run the full Airbnb neighbourhood summary pipeline."""
    cfg = PipelineConfig()

    typer.echo("Reading raw data...")
    listings = read_csv_checked(cfg.listings_path)
    segments = read_csv_checked(cfg.segments_path)

    typer.echo("Handling PII...")
    listings = handle_pii(listings)

    typer.echo("Transforming data...")
    summary = build_neighbourhood_summary(listings, segments)

    typer.echo("Validating output...")
    validate_summary(summary)

    typer.echo("Writing output CSV...")
    cfg.output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(cfg.output_path, index=False)

    typer.echo("Writing report...")
    cfg.report_path.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# HW01-A Run Report

            Generated: {datetime.now().isoformat()} UTC

            ## Summary

            - Neighbourhoods processed: {len(summary)}
            - Total listings: {summary['num_listings'].sum()}
            - Average price across all neighbourhoods: {summary['avg_price'].mean():.2f}

            ## Output

            Saved to: `{cfg.output_path}`

            ## Validation

            All checks passed!
        """
    cfg.report_path.write_text(report)
    typer.echo(f"Done. Output: {cfg.output_path}")
    
@app.command()
def version():
    """Print the package version."""
    from airbnb_ops import __version__
    typer.echo(__version__)