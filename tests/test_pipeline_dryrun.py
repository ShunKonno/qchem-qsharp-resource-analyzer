"""
Test pipeline dry run to ensure CSV output is generated.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chemistry_io import make_broombridge_stub
from algo_specs import expand_grid
from pipeline import run_batch

class TestPipelineDryRun:
    """Test pipeline dry run functionality."""
    
    def test_pipeline_csv_generation(self):
        """Test that pipeline generates CSV output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test directories
            broombridge_dir = temp_path / "broombridge"
            data_dir = temp_path / "data"
            done_dir = temp_path / ".done"
            
            broombridge_dir.mkdir()
            data_dir.mkdir()
            done_dir.mkdir()
            
            # Create test molecules
            test_molecules = ["H2", "H2O", "CH4"]
            
            # Create stub Broombridge files
            for mol_id in test_molecules:
                make_broombridge_stub(str(broombridge_dir), mol_id)
            
            # Create simple test grid
            test_grid = {
                "basis": ["STO-3G"],
                "active_space": ["full"],
                "encoding": ["JW"],
                "decomposition": ["Trotter"],
                "target_error_mHa": [1.6],
                "phys_error_rate": [1e-4]
            }
            
            # Expand grid
            specs = [s.model_dump() for s in expand_grid(test_grid)]
            assert len(specs) == 1
            
            # Run batch
            output_csv = str(data_dir / "test_results.csv")
            results = run_batch(
                molecules=test_molecules,
                specs=specs,
                broombridge_dir=str(broombridge_dir),
                output_csv=output_csv,
                done_dir=str(done_dir),
                resume=False
            )
            
            # Check results
            assert len(results) == 3  # 3 molecules × 1 spec
            assert Path(output_csv).exists()
            
            # Check CSV content
            df = pd.read_csv(output_csv)
            assert len(df) == 3
            assert list(df.columns) == [
                'molecule_id', 'basis', 'active_space', 'encoding', 'decomposition',
                'target_error_mHa', 'phys_error_rate', 'logical_qubits', 't_count',
                'circuit_depth', 'est_runtime_sec', 'physical_qubits', 'physical_runtime_sec'
            ]
            
            # Check molecule IDs
            assert set(df['molecule_id']) == set(test_molecules)
            
            # Check that all specs are the same
            assert all(df['basis'] == 'STO-3G')
            assert all(df['encoding'] == 'JW')
            assert all(df['decomposition'] == 'Trotter')
    
    def test_resume_functionality(self):
        """Test that resume functionality works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test directories
            broombridge_dir = temp_path / "broombridge"
            data_dir = temp_path / "data"
            done_dir = temp_path / ".done"
            
            broombridge_dir.mkdir()
            data_dir.mkdir()
            done_dir.mkdir()
            
            # Create test molecules
            test_molecules = ["H2", "H2O"]
            
            # Create stub Broombridge files
            for mol_id in test_molecules:
                make_broombridge_stub(str(broombridge_dir), mol_id)
            
            # Create test grid
            test_grid = {
                "basis": ["STO-3G", "6-31G"],
                "active_space": ["full"],
                "encoding": ["JW"],
                "decomposition": ["Trotter"],
                "target_error_mHa": [1.6],
                "phys_error_rate": [1e-4]
            }
            
            # Expand grid
            specs = [s.model_dump() for s in expand_grid(test_grid)]
            assert len(specs) == 2
            
            # First run
            output_csv = str(data_dir / "test_results.csv")
            results1 = run_batch(
                molecules=test_molecules,
                specs=specs,
                broombridge_dir=str(broombridge_dir),
                output_csv=output_csv,
                done_dir=str(done_dir),
                resume=False
            )
            
            assert len(results1) == 4  # 2 molecules × 2 specs
            
            # Second run with resume
            results2 = run_batch(
                molecules=test_molecules,
                specs=specs,
                broombridge_dir=str(broombridge_dir),
                output_csv=output_csv,
                done_dir=str(done_dir),
                resume=True
            )
            
            # Should return empty list since all tasks are done
            assert len(results2) == 0
            
            # Check that done flags were created
            done_files = list(done_dir.glob("*.done"))
            assert len(done_files) == 4  # 2 molecules × 2 specs
    
    def test_error_handling(self):
        """Test that pipeline handles errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test directories
            broombridge_dir = temp_path / "broombridge"
            data_dir = temp_path / "data"
            done_dir = temp_path / ".done"
            
            broombridge_dir.mkdir()
            data_dir.mkdir()
            done_dir.mkdir()
            
            # Create test molecules (including one that won't have Broombridge file)
            test_molecules = ["H2", "NONEXISTENT", "CH4"]
            
            # Create stub Broombridge files for only some molecules
            for mol_id in ["H2", "CH4"]:
                make_broombridge_stub(str(broombridge_dir), mol_id)
            
            # Create test grid
            test_grid = {
                "basis": ["STO-3G"],
                "active_space": ["full"],
                "encoding": ["JW"],
                "decomposition": ["Trotter"],
                "target_error_mHa": [1.6],
                "phys_error_rate": [1e-4]
            }
            
            # Expand grid
            specs = [s.model_dump() for s in expand_grid(test_grid)]
            
            # Run batch
            output_csv = str(data_dir / "test_results.csv")
            results = run_batch(
                molecules=test_molecules,
                specs=specs,
                broombridge_dir=str(broombridge_dir),
                output_csv=output_csv,
                done_dir=str(done_dir),
                resume=False
            )
            
            # Should have results for 2 molecules (H2 and CH4)
            assert len(results) == 2
            
            # Check CSV content
            df = pd.read_csv(output_csv)
            assert len(df) == 2
            assert set(df['molecule_id']) == {"H2", "CH4"}

if __name__ == "__main__":
    pytest.main([__file__])
