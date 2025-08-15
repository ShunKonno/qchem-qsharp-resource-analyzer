#!/usr/bin/env python3
"""
Run batch resource estimation for multiple molecules and algorithm specifications.

Usage:
    python scripts/batch_run.py --grid config/grid.yml --broombridge intermediate/broombridge --out data/resource_estimates.csv --smiles-list config/molecules.list --n-proc 4 --resume
"""

import argparse
import yaml
from pathlib import Path
import sys
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algo_specs import expand_grid
from pipeline import run_batch
from utils import setup_logging

def main():
    parser = argparse.ArgumentParser(
        description="Run batch quantum resource estimation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/batch_run.py --grid config/grid.yml --broombridge intermediate/broombridge --out data/resource_estimates.csv --smiles-list config/molecules.list --n-proc 4 --resume
        """)
    
    parser.add_argument("--grid", required=True, help="Path to grid configuration YAML")
    parser.add_argument("--broombridge", required=True, help="Directory containing Broombridge files")
    parser.add_argument("--out", required=True, help="Output CSV file path")
    parser.add_argument("--smiles-list", required=True, help="Path to molecules list file")
    parser.add_argument("--n-proc", type=int, default=1, help="Number of parallel processes")
    parser.add_argument("--resume", action="store_true", help="Resume from previous runs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    if not Path(args.grid).exists():
        logger.error(f"Grid configuration file not found: {args.grid}")
        sys.exit(1)
    
    if not Path(args.broombridge).exists():
        logger.error(f"Broombridge directory not found: {args.broombridge}")
        sys.exit(1)
    
    if not Path(args.smiles_list).exists():
        logger.error(f"Molecules list file not found: {args.smiles_list}")
        sys.exit(1)
    
    # Load configuration
    try:
        with open(args.grid, 'r') as f:
            grid = yaml.safe_load(f)
        logger.info(f"Loaded grid configuration: {list(grid.keys())}")
    except Exception as e:
        logger.error(f"Error loading grid configuration: {e}")
        sys.exit(1)
    
    # Expand grid to specifications
    try:
        specs = [s.model_dump() for s in expand_grid(grid)]
        logger.info(f"Expanded grid to {len(specs)} specifications")
    except Exception as e:
        logger.error(f"Error expanding grid: {e}")
        sys.exit(1)
    
    # Load molecules
    try:
        with open(args.smiles_list, 'r') as f:
            molecules = [line.split()[0] for line in f.readlines() 
                        if line.strip() and not line.startswith("#")]
        logger.info(f"Loaded {len(molecules)} molecules")
    except Exception as e:
        logger.error(f"Error loading molecules: {e}")
        sys.exit(1)
    
    # Setup output and done directories
    output_csv = Path(args.out)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    done_dir = Path("data/.done")
    done_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate total tasks
    total_tasks = len(molecules) * len(specs)
    logger.info(f"Total tasks: {len(molecules)} molecules × {len(specs)} specs = {total_tasks}")
    
    if args.resume:
        logger.info("Resume mode enabled - will skip completed tasks")
    
    # Run batch estimation
    try:
        results = run_batch(
            molecules=molecules,
            specs=specs,
            broombridge_dir=args.broombridge,
            output_csv=str(output_csv),
            done_dir=str(done_dir),
            resume=args.resume
        )
        
        logger.info(f"Batch run completed successfully: {len(results)} results written to {output_csv}")
        
    except Exception as e:
        logger.error(f"Batch run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
