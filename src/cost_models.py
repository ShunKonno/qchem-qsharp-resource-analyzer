def logical_to_physical(logical_qubits: int, t_count: float, ft: dict) -> dict:
    """Convert logical resources to physical resources.
    
    TODO: Replace with realistic Surface code approximation:
    - Code distance d calculation
    - T-Factory overhead
    - Parallelization factors
    
    Args:
        logical_qubits: Number of logical qubits
        t_count: T-count estimate
        ft: Fault tolerance configuration
        
    Returns:
        Dictionary with physical resource estimates
    """
    # Simplified conversion - replace with Surface code calculations
    physical_error_rate = ft.get("physical_error_rate", 1e-4)
    
    # Dummy scaling factors (replace with actual Surface code math)
    if physical_error_rate <= 1e-4:
        qubit_overhead = 100  # Surface code with d=7
        time_overhead = 3e4   # T-Factory and error correction
    else:
        qubit_overhead = 200  # Higher overhead for worse error rates
        time_overhead = 5e4
    
    physical_qubits = int(logical_qubits * qubit_overhead)
    physical_runtime_sec = float(t_count / time_overhead)
    
    return {
        "physical_qubits": physical_qubits, 
        "physical_runtime_sec": physical_runtime_sec
    }
