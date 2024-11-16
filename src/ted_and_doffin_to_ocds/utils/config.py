from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration settings for notice conversion."""

    input_path: Path
    output_folder: Path
    ocid_prefix: str
    scheme: str
    db_path: Path
    clear_db: bool
    log_level: str
