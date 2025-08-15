from pathlib import Path
from typing import List

def smiles_list(path: str) -> List[str]:
    """Read SMILES list from file, skipping comments and empty lines."""
    return [line.strip() for line in Path(path).read_text().splitlines() 
            if line.strip() and not line.startswith("#")]

def make_broombridge_stub(out_dir: str, mol_id: str) -> str:
    """Create a stub Broombridge file for the given molecule ID.
    
    TODO: Replace with actual PySCF/NWChem → Broombridge conversion
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    f = out / f"{mol_id}.yaml"
    
    # Stub Broombridge content
    content = f"""# Broombridge stub for {mol_id}
# TODO: Replace with actual PySCF/NWChem output
document:
  molecule: {mol_id}
  basis_set: STO-3G
  geometry:
    units: angstrom
    atoms:
      - H: [0.0, 0.0, 0.0]
  hamiltonian:
    name: "electronic"
    one_electron_integrals:
      - [0.0, 0.0]
    two_electron_integrals:
      - [0.0, 0.0, 0.0, 0.0]
"""
    
    f.write_text(content)
    return str(f)
