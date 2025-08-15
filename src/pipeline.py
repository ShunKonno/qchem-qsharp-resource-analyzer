from pathlib import Path
from .cost_models import logical_to_physical
from .estimator import estimate
from .utils import done_flag_path, write_row_csv, calculate_spec_hash
import logging

logger = logging.getLogger(__name__)

def run_one(mol_id: str, broombridge_path: str, spec: dict) -> dict:
    """Run resource estimation for one molecule with one algorithm specification.
    
    Args:
        mol_id: Molecule identifier
        broombridge_path: Path to Broombridge YAML file
        spec: Algorithm specification dictionary
        
    Returns:
        Dictionary with all results (molecule + algorithm + resources)
    """
    try:
        # Run quantum resource estimation
        est = estimate(broombridge_path, spec)
        
        # Convert logical to physical resources
        phys = logical_to_physical(
            est["logical_qubits"], 
            est["t_count"], 
            spec["fault_tolerance"]
        )
        
        # Combine all results
        result = {
            "molecule_id": mol_id,
            "basis": spec["basis"],
            "active_space": spec["active_space"],
            "encoding": spec["encoding"],
            "decomposition": spec["decomposition"],
            "target_error_mHa": spec["target_error_mHa"],
            "phys_error_rate": spec["fault_tolerance"]["physical_error_rate"],
            **est,  # logical resources
            **phys   # physical resources
        }
        
        logger.info(f"Completed estimation for {mol_id} with {spec['basis']}/{spec['encoding']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed estimation for {mol_id}: {e}")
        raise

def run_batch(molecules: list, specs: list, broombridge_dir: str, 
              output_csv: str, done_dir: str, resume: bool = True) -> list:
    """Run batch resource estimation for multiple molecules and specifications.
    
    Args:
        molecules: List of molecule IDs
        specs: List of algorithm specifications
        broombridge_dir: Directory containing Broombridge files
        output_csv: Output CSV file path
        done_dir: Directory for done flags
        resume: Whether to resume from previous runs
        
    Returns:
        List of completed results
    """
    results = []
    total_tasks = len(molecules) * len(specs)
    completed = 0
    
    logger.info(f"Starting batch run: {len(molecules)} molecules × {len(specs)} specs = {total_tasks} tasks")
    
    for mol_id in molecules:
        broombridge_path = Path(broombridge_dir) / f"{mol_id}.yaml"
        
        if not broombridge_path.exists():
            logger.warning(f"Broombridge file not found: {broombridge_path}")
            continue
            
        for spec in specs:
            spec_hash = calculate_spec_hash(spec)
            done_flag = done_flag_path(done_dir, mol_id, spec_hash)
            
            # Check if already completed
            if resume and done_flag.exists():
                logger.debug(f"Skipping completed task: {mol_id} with {spec['basis']}")
                completed += 1
                continue
            
            try:
                # Run estimation
                result = run_one(mol_id, str(broombridge_path), spec)
                results.append(result)
                
                # Write to CSV
                write_row_csv(output_csv, result, header=(len(results) == 1))
                
                # Mark as done
                done_flag.touch()
                completed += 1
                
                logger.info(f"Progress: {completed}/{total_tasks} tasks completed")
                
            except Exception as e:
                logger.error(f"Task failed: {mol_id} with {spec['basis']}: {e}")
                continue
    
    logger.info(f"Batch run completed: {len(results)} successful results")
    return results
