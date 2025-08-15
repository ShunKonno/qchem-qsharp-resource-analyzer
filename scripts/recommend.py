#!/usr/bin/env python3
"""
Recommend optimal algorithm settings based on resource estimation results.

Usage:
    python scripts/recommend.py --molecule H2O --objective Min-T --chem-acc 1.6
"""

import argparse
import pandas as pd
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Recommend optimal algorithm settings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/recommend.py --molecule H2O --objective Min-T --chem-acc 1.6
    python scripts/recommend.py --molecule CH4 --objective Min-Depth --chem-acc 0.8
        """)
    
    parser.add_argument("--csv", default="data/resource_estimates.csv", 
                       help="Path to resource estimates CSV file")
    parser.add_argument("--molecule", required=True, 
                       help="Molecule ID to analyze")
    parser.add_argument("--objective", 
                       choices=["Min-T", "Min-Depth", "Min-Runtime", "Min-Physical-Qubits"],
                       default="Min-T",
                       help="Optimization objective")
    parser.add_argument("--chem-acc", type=float, default=1.6,
                       help="Maximum acceptable chemical error (mHa)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed results")
    
    args = parser.parse_args()
    
    # Check if CSV exists
    if not Path(args.csv).exists():
        print(f"Error: Resource estimates CSV file not found: {args.csv}")
        print("Please run batch estimation first:")
        print("  python scripts/batch_run.py --grid config/grid.yml --broombridge intermediate/broombridge --out data/resource_estimates.csv --smiles-list config/molecules.list")
        sys.exit(1)
    
    # Load data
    try:
        df = pd.read_csv(args.csv)
        print(f"Loaded {len(df)} resource estimates from {args.csv}")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)
    
    # Filter by molecule and chemical accuracy
    df_filtered = df[
        (df["molecule_id"] == args.molecule) & 
        (df["target_error_mHa"] <= args.chem_acc)
    ]
    
    if df_filtered.empty:
        print(f"No results found for molecule '{args.molecule}' with chemical accuracy ≤ {args.chem_acc} mHa")
        print(f"Available molecules: {sorted(df['molecule_id'].unique())}")
        print(f"Available error thresholds: {sorted(df['target_error_mHa'].unique())}")
        sys.exit(1)
    
    print(f"Found {len(df_filtered)} configurations for {args.molecule} (chem acc ≤ {args.chem_acc} mHa)")
    
    # Map objective to column
    objective_map = {
        "Min-T": "t_count",
        "Min-Depth": "circuit_depth", 
        "Min-Runtime": "est_runtime_sec",
        "Min-Physical-Qubits": "physical_qubits"
    }
    
    target_column = objective_map[args.objective]
    
    # Find optimal setting
    optimal = df_filtered.loc[df_filtered[target_column].idxmin()]
    
    print(f"\n🎯 Optimal setting for {args.objective}:")
    print("=" * 50)
    
    # Display key parameters
    key_params = [
        "basis", "active_space", "encoding", "decomposition", 
        "target_error_mHa", "phys_error_rate"
    ]
    
    for param in key_params:
        if param in optimal:
            print(f"{param:20}: {optimal[param]}")
    
    print("-" * 50)
    
    # Display resource estimates
    resource_cols = [
        "logical_qubits", "t_count", "circuit_depth", "est_runtime_sec",
        "physical_qubits", "physical_runtime_sec"
    ]
    
    print("Resource Estimates:")
    for col in resource_cols:
        if col in optimal:
            value = optimal[col]
            if col in ["t_count", "circuit_depth"]:
                print(f"{col:20}: {value:,.0f}")
            elif col in ["est_runtime_sec", "physical_runtime_sec"]:
                print(f"{col:20}: {value:,.0f} sec")
            else:
                print(f"{col:20}: {value:,}")
    
    # Show comparison with other settings
    if args.verbose and len(df_filtered) > 1:
        print(f"\n📊 Comparison with other {len(df_filtered)-1} settings:")
        print("-" * 50)
        
        # Sort by objective and show top 5
        df_sorted = df_filtered.sort_values(target_column)
        for i, (_, row) in enumerate(df_sorted.head().iterrows()):
            marker = "🥇" if i == 0 else f"{i+1:2d}."
            print(f"{marker} {row['basis']:8} {row['encoding']:2} {row['decomposition']:8} "
                  f"{row['target_error_mHa']:5.1f} → {row[target_column]:,.0f}")

if __name__ == "__main__":
    main()
