from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
import itertools
import hashlib
import json

Encoding = Literal["JW", "BK"]
Decomp = Literal["Trotter", "Qubitization"]

class FaultTolerance(BaseModel):
    scheme: Literal["surface_code"] = "surface_code"
    physical_error_rate: float = 1e-4
    cycle_time_ns: int = 100
    max_factories: int = 4

class AlgoSpec(BaseModel):
    basis: str
    active_space: str
    encoding: Encoding
    decomposition: Decomp
    target_error_mHa: float
    fault_tolerance: FaultTolerance

    def hash(self) -> str:
        d = self.model_dump()
        s = json.dumps(d, sort_keys=True).encode()
        return hashlib.sha1(s).hexdigest()[:16]

def expand_grid(grid: Dict[str, Any]) -> List[AlgoSpec]:
    out = []
    keys = ["basis", "active_space", "encoding", "decomposition", "target_error_mHa"]
    combos = itertools.product(*(grid[k] if isinstance(grid[k], list) else [grid[k]] for k in keys))
    ft = FaultTolerance(
        scheme="surface_code",
        physical_error_rate=float(grid.get("phys_error_rate", [1e-4])[0]),
        cycle_time_ns=100, 
        max_factories=4
    )
    for basis, active, enc, decomp, terr in combos:
        out.append(AlgoSpec(
            basis=basis, 
            active_space=active, 
            encoding=enc,
            decomposition=decomp, 
            target_error_mHa=float(terr),
            fault_tolerance=ft
        ))
    return out
