from dataclasses import dataclass, field
from pathlib import Path

# This is the src/airbnb_ops/ directory
_PACKAGE_DIR = Path(__file__).parent

# Walk up to the project root (src/airbnb_ops -> src -> project root)
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent

@dataclass
class PipelineConfig:
    listings_path: Path = field(default_factory=lambda: _PROJECT_ROOT / "data/raw/listings_sample.csv")
    segments_path: Path = field(default_factory=lambda: _PROJECT_ROOT / "data/raw/neighbourhood_segments.csv")
    output_path: Path = field(default_factory=lambda: _PROJECT_ROOT / "data/processed/airbnb_neighbourhood_summary.csv")
    report_path: Path = field(default_factory=lambda: _PROJECT_ROOT / "reports/hw01_a_run_report.md")