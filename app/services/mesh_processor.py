"""
Mesh processing service for Q_FEA
"""

import numpy as np
import logging
from pathlib import Path
import time

try:
    import meshio
    import vtk
    from vtk.util import numpy_support
    MESH_LIBRARIES_AVAILABLE = True
except ImportError:
    MESH_LIBRARIES_AVAILABLE = False
    logging.warning("Mesh processing libraries not available. Install meshio and vtk.")

from qfea_core.classical_utils.generate_mesh import compute_stiffness_mass_matrices
from qfea_core.classical_utils.hamiltonian_prep import compute_H

logger = logging.getLogger(__name__)

class MeshProcessor:
    """Service for processing finite element meshes"""
    
    def __init__(self):
        self.supported_formats = {'.vtk', '.mesh', '.msh', '.obj', '.stl', '.ply'}
    
    def get_mesh_info(self, file_path):
        """Extract basic information from mesh file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Mesh file not found: {file_path}")
            
            file_size = file_path.stat().st_size
            extension = file_path.suffix.lower()
            
            if not MESH_LIBRARIES_AVAILABLE:
                # Fallback: basic file info only
                return {
                    'filename': file_path.name,
                    'file_size': file_size,
                    'format': extension,
                    'vertices': 'Unknown',
                    'elements': 'Unknown',
                    'dimensions': 3,
                    'bounding_box': None
                }
            
            # Load mesh using meshio
            mesh = meshio.read(file_path)
            
            vertices = mesh.points
            num_vertices = len(vertices)
            
            # Count elements
            num_elements = sum(len(cells.data) for cells in mesh.cells)
            
            # Calculate bounding box
            bbox_min = np.min(vertices, axis=0)
            bbox_max = np.max(vertices, axis=0)
            dimensions = len(bbox_min)
            
            # Estimate mesh quality metrics
            volume = self._estimate_volume(bbox_min, bbox_max)
            
            mesh_info = {
                'filename': file_path.name,
                'file_size': file_size,
                'format': extension,
                'vertices': num_vertices,
                'elements': num_elements,
                'dimensions': dimensions,
                'bounding_box': {
                    'min': bbox_min.tolist(),
                    'max': bbox_max.tolist(),
                    'size': (bbox_max - bbox_min).tolist()
                },
                'estimated_volume': volume,
                'cell_types': [cell.type for cell in mesh.cells]
            }
            
            logger.info(f"Mesh info extracted: {num_vertices} vertices, {num_elements} elements")
            return mesh_info
            
        except Exception as e:
            logger.error(f"Error extracting mesh info: {str(e)}")
            raise
    
    def compute_matrices(self, file_path, material_properties):
        """Compute stiffness and mass matrices from mesh"""
        try:
            start_time = time.time()
            
            # Use the existing function from your codebase
            logger.info(f"Computing matrices for {file_path}")
            
            # This calls your existing function
            K, M = compute_stiffness_mass_matrices(str(file_path))
            
            computation_time = time.time() - start_time
            
            # Calculate matrix properties
            dimension = K.shape[0]
            dof_count = dimension * 3  # Assuming 3D displacement
            
            # Calculate condition number (approximation for large matrices)
            if dimension < 1000:
                try:
                    eigenvals_k = np.linalg.eigvals(K)
                    eigenvals_k = eigenvals_k[eigenvals_k > 1e-10]  # Remove near-zero eigenvalues
                    condition_number = np.max(eigenvals_k) / np.min(eigenvals_k)
                except (np.linalg.LinAlgError, ValueError, RuntimeError):
                    condition_number = self._estimate_condition_number(K)
            else:
                condition_number = self._estimate_condition_number(K)
            
            # Calculate sparsity
            sparsity = self._calculate_sparsity(K)
            
            result = {
                'stiffness_matrix': K,
                'mass_matrix': M,
                'dimension': dimension,
                'dof_count': dof_count,
                'condition_number': float(condition_number),
                'sparsity': sparsity,
                'computation_time': computation_time,
                'material_properties': material_properties
            }
            
            logger.info(f"Matrices computed in {computation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error computing matrices: {str(e)}")
            raise
    
    def _estimate_volume(self, bbox_min, bbox_max):
        """Estimate volume from bounding box"""
        size = bbox_max - bbox_min
        return float(np.prod(size))
    
    def _estimate_condition_number(self, matrix):
        """Estimate condition number for large matrices"""
        try:
            # Use power iteration to estimate largest eigenvalue
            n = matrix.shape[0]
            v = np.random.rand(n)
            
            for _ in range(10):  # Power iterations
                v = matrix @ v
                v = v / np.linalg.norm(v)
            
            lambda_max = v.T @ matrix @ v
            
            # Estimate smallest eigenvalue (very rough approximation)
            lambda_min = np.trace(matrix) / n * 0.01  # Rough estimate
            
            return lambda_max / max(lambda_min, 1e-10)

        except (np.linalg.LinAlgError, ValueError, RuntimeError):
            # Fallback: use diagonal dominance
            diag = np.abs(np.diag(matrix))
            off_diag = np.sum(np.abs(matrix), axis=1) - diag
            return np.max(diag) / np.min(diag[diag > 1e-10])
    
    def _calculate_sparsity(self, matrix):
        """Calculate matrix sparsity (fraction of non-zero elements)"""
        try:
            total_elements = matrix.size
            non_zero_elements = np.count_nonzero(np.abs(matrix) > 1e-12)
            return non_zero_elements / total_elements
        except:
            return 0.5  # Default estimate
    
    def validate_mesh_file(self, file_path):
        """Validate mesh file format and integrity"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, "File does not exist"
            
            if file_path.suffix.lower() not in self.supported_formats:
                return False, f"Unsupported format: {file_path.suffix}"
            
            if file_path.stat().st_size == 0:
                return False, "File is empty"
            
            # Try to read the mesh
            if MESH_LIBRARIES_AVAILABLE:
                try:
                    mesh = meshio.read(file_path)
                    if len(mesh.points) == 0:
                        return False, "Mesh contains no vertices"
                    if len(mesh.cells) == 0:
                        return False, "Mesh contains no elements"
                except (IOError, ValueError, KeyError, RuntimeError):
                    return False, "Invalid mesh file format"
            
            return True, "Valid mesh file"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_mesh_statistics(self, file_path):
        """Get detailed mesh statistics"""
        try:
            if not MESH_LIBRARIES_AVAILABLE:
                return {"error": "Mesh libraries not available"}
            
            mesh = meshio.read(file_path)
            vertices = mesh.points
            
            stats = {
                'vertex_statistics': {
                    'count': len(vertices),
                    'mean': np.mean(vertices, axis=0).tolist(),
                    'std': np.std(vertices, axis=0).tolist(),
                    'min': np.min(vertices, axis=0).tolist(),
                    'max': np.max(vertices, axis=0).tolist()
                },
                'element_statistics': {
                    'total_count': sum(len(cells.data) for cells in mesh.cells),
                    'types': {}
                }
            }
            
            # Element type statistics
            for cells in mesh.cells:
                cell_type = cells.type
                count = len(cells.data)
                stats['element_statistics']['types'][cell_type] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting mesh statistics: {str(e)}")
            return {"error": str(e)}