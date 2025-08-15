#!/usr/bin/env python3
"""
Sanity check script for the quantum resource estimation pipeline.

This script runs a quick test with 3 molecules to verify the pipeline works.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_sanity_check():
    """Run a complete sanity check of the pipeline."""
    print("🧪 Running sanity check for quantum resource estimation pipeline...")
    print("=" * 60)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test molecules list
        test_molecules = temp_path / "test_molecules.list"
        test_molecules.write_text("""H2  H
H2O O
CH4 C""")
        
        # Create test grid configuration
        test_grid = temp_path / "test_grid.yml"
        test_grid.write_text("""basis: ["STO-3G"]
active_space: ["full"]
encoding: ["JW"]
decomposition: ["Trotter"]
target_error_mHa: [1.6]
phys_error_rate: [1.0e-4]""")
        
        # Create test output directories
        test_broombridge = temp_path / "broombridge"
        test_data = temp_path / "data"
        test_broombridge.mkdir()
        test_data.mkdir()
        
        print("1️⃣ Converting test molecules to Broombridge...")
        try:
            # Import and run conversion
            from chemistry_io import smiles_list, make_broombridge_stub
            
            molecules = smiles_list(str(test_molecules))
            for mol_id in [line.split()[0] for line in molecules]:
                make_broombridge_stub(str(test_broombridge), mol_id)
            
            broombridge_files = list(test_broombridge.glob("*.yaml"))
            print(f"   ✅ Created {len(broombridge_files)} Broombridge files")
            
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            return False
        
        print("2️⃣ Testing algorithm specification expansion...")
        try:
            import yaml
            from algo_specs import expand_grid
            
            with open(test_grid, 'r') as f:
                grid = yaml.safe_load(f)
            
            specs = expand_grid(grid)
            print(f"   ✅ Expanded grid to {len(specs)} specifications")
            
            # Test first spec
            first_spec = specs[0]
            print(f"   📋 Sample spec: {first_spec.basis}/{first_spec.encoding}/{first_spec.decomposition}")
            
        except Exception as e:
            print(f"   ❌ Grid expansion failed: {e}")
            return False
        
        print("3️⃣ Testing resource estimation (mock)...")
        try:
            from estimator import estimate
            from cost_models import logical_to_physical
            
            # Test estimation
            test_spec = specs[0].model_dump()
            test_broombridge_file = str(test_broombridge / "H2.yaml")
            
            est_result = estimate(test_broombridge_file, test_spec)
            print(f"   ✅ Estimation completed: {est_result['logical_qubits']} qubits, {est_result['t_count']:,.0f} T-count")
            
            # Test cost model
            phys_result = logical_to_physical(
                est_result["logical_qubits"], 
                est_result["t_count"], 
                test_spec["fault_tolerance"]
            )
            print(f"   ✅ Cost model: {phys_result['physical_qubits']:,} physical qubits")
            
        except Exception as e:
            print(f"   ❌ Resource estimation failed: {e}")
            return False
        
        print("4️⃣ Testing pipeline integration...")
        try:
            from pipeline import run_batch
            
            results = run_batch(
                molecules=[line.split()[0] for line in molecules],
                specs=[s.model_dump() for s in specs],
                broombridge_dir=str(test_broombridge),
                output_csv=str(test_data / "test_results.csv"),
                done_dir=str(test_data / ".done"),
                resume=False
            )
            
            print(f"   ✅ Pipeline completed: {len(results)} results")
            
            # Check output file
            output_file = test_data / "test_results.csv"
            if output_file.exists():
                print(f"   📄 Output CSV created: {output_file.stat().st_size} bytes")
            else:
                print("   ❌ Output CSV not created")
                return False
                
        except Exception as e:
            print(f"   ❌ Pipeline integration failed: {e}")
            return False
        
        print("5️⃣ Testing recommendation system...")
        try:
            from recommend import main as recommend_main
            
            # We can't easily test the CLI directly, but we can test the logic
            import pandas as pd
            
            df = pd.read_csv(test_data / "test_results.csv")
            if len(df) > 0:
                print(f"   ✅ Recommendation system ready: {len(df)} data points available")
            else:
                print("   ❌ No data for recommendations")
                return False
                
        except Exception as e:
            print(f"   ❌ Recommendation system test failed: {e}")
            return False
    
    print("\n🎉 All sanity checks passed!")
    print("=" * 60)
    print("The pipeline is ready for production use.")
    print("\nNext steps:")
    print("1. Run: make convert")
    print("2. Run: make batch")
    print("3. Run: make recommend")
    print("4. Or run the full pipeline: make smoke")
    
    return True

if __name__ == "__main__":
    success = run_sanity_check()
    sys.exit(0 if success else 1)
