"""
Test Pydantic schemas and grid expansion functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algo_specs import AlgoSpec, FaultTolerance, expand_grid

class TestFaultTolerance:
    """Test FaultTolerance model."""
    
    def test_default_values(self):
        """Test default fault tolerance values."""
        ft = FaultTolerance()
        assert ft.scheme == "surface_code"
        assert ft.physical_error_rate == 1e-4
        assert ft.cycle_time_ns == 100
        assert ft.max_factories == 4
    
    def test_custom_values(self):
        """Test custom fault tolerance values."""
        ft = FaultTolerance(
            physical_error_rate=1e-3,
            cycle_time_ns=200,
            max_factories=8
        )
        assert ft.physical_error_rate == 1e-3
        assert ft.cycle_time_ns == 200
        assert ft.max_factories == 8

class TestAlgoSpec:
    """Test AlgoSpec model."""
    
    def test_valid_spec(self):
        """Test valid algorithm specification."""
        ft = FaultTolerance()
        spec = AlgoSpec(
            basis="STO-3G",
            active_space="full",
            encoding="JW",
            decomposition="Trotter",
            target_error_mHa=1.6,
            fault_tolerance=ft
        )
        
        assert spec.basis == "STO-3G"
        assert spec.encoding == "JW"
        assert spec.decomposition == "Trotter"
        assert spec.target_error_mHa == 1.6
    
    def test_hash_consistency(self):
        """Test that hash is consistent for same spec."""
        ft = FaultTolerance()
        spec1 = AlgoSpec(
            basis="STO-3G",
            active_space="full",
            encoding="JW",
            decomposition="Trotter",
            target_error_mHa=1.6,
            fault_tolerance=ft
        )
        
        spec2 = AlgoSpec(
            basis="STO-3G",
            active_space="full",
            encoding="JW",
            decomposition="Trotter",
            target_error_mHa=1.6,
            fault_tolerance=ft
        )
        
        assert spec1.hash() == spec2.hash()
    
    def test_hash_uniqueness(self):
        """Test that different specs have different hashes."""
        ft = FaultTolerance()
        spec1 = AlgoSpec(
            basis="STO-3G",
            active_space="full",
            encoding="JW",
            decomposition="Trotter",
            target_error_mHa=1.6,
            fault_tolerance=ft
        )
        
        spec2 = AlgoSpec(
            basis="6-31G",  # Different basis
            active_space="full",
            encoding="JW",
            decomposition="Trotter",
            target_error_mHa=1.6,
            fault_tolerance=ft
        )
        
        assert spec1.hash() != spec2.hash()

class TestGridExpansion:
    """Test grid expansion functionality."""
    
    def test_simple_grid(self):
        """Test simple grid with single values."""
        grid = {
            "basis": "STO-3G",
            "active_space": "full",
            "encoding": "JW",
            "decomposition": "Trotter",
            "target_error_mHa": 1.6,
            "phys_error_rate": [1e-4]
        }
        
        specs = expand_grid(grid)
        assert len(specs) == 1
        
        spec = specs[0]
        assert spec.basis == "STO-3G"
        assert spec.encoding == "JW"
        assert spec.target_error_mHa == 1.6
    
    def test_multi_value_grid(self):
        """Test grid with multiple values."""
        grid = {
            "basis": ["STO-3G", "6-31G"],
            "active_space": "full",
            "encoding": ["JW", "BK"],
            "decomposition": "Trotter",
            "target_error_mHa": [0.8, 1.6],
            "phys_error_rate": [1e-4]
        }
        
        specs = expand_grid(grid)
        # 2 × 1 × 2 × 1 × 2 = 8 combinations
        assert len(specs) == 8
        
        # Check that all combinations are present
        bases = set(spec.basis for spec in specs)
        encodings = set(spec.encoding for spec in specs)
        errors = set(spec.target_error_mHa for spec in specs)
        
        assert bases == {"STO-3G", "6-31G"}
        assert encodings == {"JW", "BK"}
        assert errors == {0.8, 1.6}
    
    def test_fault_tolerance_inheritance(self):
        """Test that fault tolerance is properly inherited."""
        grid = {
            "basis": "STO-3G",
            "active_space": "full",
            "encoding": "JW",
            "decomposition": "Trotter",
            "target_error_mHa": 1.6,
            "phys_error_rate": [1e-3, 1e-4]
        }
        
        specs = expand_grid(grid)
        assert len(specs) == 2
        
        # Both should have same fault tolerance scheme
        for spec in specs:
            assert spec.fault_tolerance.scheme == "surface_code"
            assert spec.fault_tolerance.cycle_time_ns == 100
            assert spec.fault_tolerance.max_factories == 4

if __name__ == "__main__":
    pytest.main([__file__])
