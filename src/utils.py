from pathlib import Path
import json
import hashlib
import csv
import logging

def setup_logging(log_file: str = None, level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

def done_flag_path(root: str, mol_id: str, spec_hash: str) -> Path:
    """Get path for done flag file to track completed calculations."""
    p = Path(root) / f"{mol_id}-{spec_hash}.done"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def write_row_csv(csv_path: str, row: dict, header: bool = False):
    """Write a row to CSV file, creating directory if needed."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = 'w' if header else 'a'
    with open(csv_path, mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if header:
            w.writeheader()
        w.writerow(row)

def calculate_spec_hash(spec: dict) -> str:
    """Calculate hash for algorithm specification."""
    # Sort keys for consistent hashing
    sorted_spec = dict(sorted(spec.items()))
    spec_str = json.dumps(sorted_spec, sort_keys=True)
    return hashlib.sha1(spec_str.encode()).hexdigest()[:16]
