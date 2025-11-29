"""
Lattice Structure for Memory Palace.

This module implements the 3D spatial organization (Chess Cube) adapted from the 
original Memory Palace NN, but fully integrated into the Digital Cortex codebase.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ChessCubeLattice:
    """
    Rigorous definition of the 8x8x8 Memory Palace structure.
    Represents a single 'Room' in the chain.
    """
    def __init__(self, size: int = 8):
        self.size = size
        self.coordinates = self._generate_coordinates()
        
    def _generate_coordinates(self) -> Dict[str, Dict[str, Any]]:
        """Generate the coordinate system for the cube."""
        coordinates = {}
        for x in range(1, self.size + 1):  # File (A-H equivalent)
            for y in range(1, self.size + 1):  # Rank (1-8)
                for z in range(1, self.size + 1):  # Height (Floor 1-8)
                    cell_key = f"{x}_{y}_{z}"
                    coordinates[cell_key] = {
                        'x': x, 'y': y, 'z': z,
                        # Parity is useful for alternating patterns/separation
                        'color_parity': (x + y + z) % 2,
                        'content': None
                    }
        return coordinates

    def get_location(self, x: int, y: int, z: int) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific location."""
        key = f"{x}_{y}_{z}"
        return self.coordinates.get(key)
        
    def is_valid_coord(self, x: int, y: int, z: int) -> bool:
        """Check if coordinates are within bounds."""
        return (1 <= x <= self.size and 
                1 <= y <= self.size and 
                1 <= z <= self.size)


class Tier2Lattice(ChessCubeLattice):
    """
    A secondary 'Shadow' Memory Palace for storing generated knowledge/explanations.
    Maps 1:1 to the primary lattice but stores 'derivative' content.
    """
    def __init__(self, size: int = 8):
        super().__init__(size)
        self.storage: Dict[str, List[Dict[str, Any]]] = {}

    def store_explanation(self, primary_coords: Tuple[int, int, int], 
                         explanation: str, 
                         context: Dict[str, Any]) -> str:
        """
        Stores an explanation in the Tier 2 lattice.
        """
        x, y, z = primary_coords
        key = f"{x}_{y}_{z}"
        
        if key not in self.storage:
            self.storage[key] = []
            
        entry = {
            "explanation": explanation,
            "context": context,
            "timestamp": context.get("timestamp")
        }
        self.storage[key].append(entry)
        return key

    def get_neighbors(self, coords: Tuple[int, int, int], radius: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieves explanations from neighboring coordinates in 3D space.
        Enables branched retrieval for richer context.
        """
        x, y, z = coords
        neighbors = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    
                    nx, ny, nz = x + dx, y + dy, z + dz
                    
                    if self.is_valid_coord(nx, ny, nz):
                        neighbor_key = f"{nx}_{ny}_{nz}"
                        if neighbor_key in self.storage:
                            neighbors.extend(self.storage[neighbor_key])
        
        return neighbors
