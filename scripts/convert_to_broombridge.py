#!/usr/bin/env python3
"""
Convert SMILES/XYZ files to Broombridge format.

Usage:
    python scripts/convert_to_broombridge.py --smiles-list config/molecules.list --out intermediate/broombridge
"""

import argparse
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chemistry_io import smiles_list, make_broombridge_stub

def main():
    parser = argparse.ArgumentParser(
        description="Convert SMILES/XYZ to Broombridge format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/convert_to_broombridge.py --smiles-list config/molecules.list --out intermediate/broombridge
        """)
    
    parser.add_argument(
        "--smiles-list", 
        required=True,
        help="Path to file containing SMILES strings (one per line)"
    )
    parser.add_argument(
        "--out", 
        required=True,
        help="Output directory for Broombridge files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.smiles_list).exists():
        print(f"Error: SMILES list file not found: {args.smiles_list}")
        sys.exit(1)
    
    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read molecules
    try:
        molecules = smiles_list(args.smiles_list)
        if args.verbose:
            print(f"Found {len(molecules)} molecules in {args.smiles_list}")
    except Exception as e:
        print(f"Error reading SMILES list: {e}")
        sys.exit(1)
    
    # Convert each molecule
    converted = 0
    for i, line in enumerate(molecules):
        if not line.strip():
            continue
            
        # Extract molecule ID (first column)
        mol_id = line.split()[0]
        
        try:
            output_file = make_broombridge_stub(args.out, mol_id)
            converted += 1
            if args.verbose:
                print(f"[{i+1:3d}] Created: {output_file}")
        except Exception as e:
            print(f"Error converting {mol_id}: {e}")
            continue
    
    print(f"Conversion complete: {converted} Broombridge files created in {args.out}")
    print(f"Note: These are stub files. Replace with actual PySCF/NWChem output.")

if __name__ == "__main__":
    main()
