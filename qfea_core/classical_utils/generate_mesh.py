"""
Classical FEA utilities for mesh generation and matrix computation
"""

import numpy as np
import logging
from scipy.sparse import csr_matrix, lil_matrix

logger = logging.getLogger(__name__)


def compute_stiffness_mass_matrices(mesh_data, material_properties):
    """
    Compute stiffness and mass matrices for FEA mesh

    Args:
        mesh_data: Dictionary containing mesh information
            - nodes: Array of node coordinates (N x 3)
            - elements: Array of element connectivity
            - num_nodes: Number of nodes
            - num_elements: Number of elements
        material_properties: Dictionary containing material properties
            - young_modulus: Young's modulus (Pa)
            - poisson_ratio: Poisson's ratio
            - density: Material density (kg/m³)

    Returns:
        Dictionary containing:
            - K: Stiffness matrix (sparse)
            - M: Mass matrix (sparse)
            - num_dofs: Number of degrees of freedom
            - computation_time: Time taken for computation
    """
    import time
    start_time = time.time()

    try:
        num_nodes = mesh_data.get('num_nodes', 0)
        num_elements = mesh_data.get('num_elements', 0)

        logger.info(f"Computing FEA matrices for {num_nodes} nodes, {num_elements} elements")

        # Number of DOFs (3 per node for 3D problems)
        num_dofs = num_nodes * 3

        # Extract material properties
        E = material_properties['young_modulus']
        nu = material_properties['poisson_ratio']
        rho = material_properties['density']

        # Compute material constants
        lambda_lame = (E * nu) / ((1 + nu) * (1 - 2 * nu))
        mu = E / (2 * (1 + nu))

        # For a simplified implementation, create sparse matrices
        # In a full implementation, this would assemble element matrices

        # Create sparse stiffness matrix (using approximation)
        K = lil_matrix((num_dofs, num_dofs))

        # Simple diagonal approximation for stiffness
        # In practice, this should be assembled from element stiffness matrices
        for i in range(num_dofs):
            K[i, i] = E * 1e-6  # Scaled for numerical stability

        # Add some off-diagonal coupling
        for i in range(0, num_dofs - 3, 3):
            for j in range(3):
                if i + j + 3 < num_dofs:
                    K[i + j, i + j + 3] = -E * 1e-7
                    K[i + j + 3, i + j] = -E * 1e-7

        # Create mass matrix (lumped mass approximation)
        M = lil_matrix((num_dofs, num_dofs))

        # Average element volume approximation
        if num_elements > 0:
            avg_element_mass = rho * (1.0 / num_elements)
        else:
            avg_element_mass = rho

        for i in range(num_dofs):
            M[i, i] = avg_element_mass

        # Convert to CSR format for efficient operations
        K = K.tocsr()
        M = M.tocsr()

        computation_time = time.time() - start_time

        logger.info(f"Matrix computation completed in {computation_time:.3f}s")
        logger.info(f"Stiffness matrix: {K.shape}, nnz={K.nnz}")
        logger.info(f"Mass matrix: {M.shape}, nnz={M.nnz}")

        return {
            'K': K,
            'M': M,
            'num_dofs': num_dofs,
            'computation_time': computation_time,
            'material_constants': {
                'lambda': lambda_lame,
                'mu': mu
            }
        }

    except Exception as e:
        logger.error(f"Error computing matrices: {e}")
        raise


def generate_simple_mesh(mesh_type='cube', size=1.0, resolution=10):
    """
    Generate a simple structured mesh for testing

    Args:
        mesh_type: Type of mesh ('cube', 'beam', 'plate')
        size: Size of the geometry
        resolution: Number of elements per dimension

    Returns:
        Dictionary containing mesh data
    """
    if mesh_type == 'cube':
        # Generate a simple cube mesh
        n = resolution
        nodes = []
        elements = []

        # Generate nodes
        for i in range(n + 1):
            for j in range(n + 1):
                for k in range(n + 1):
                    x = (i / n) * size
                    y = (j / n) * size
                    z = (k / n) * size
                    nodes.append([x, y, z])

        nodes = np.array(nodes)

        # Generate elements (hexahedrons)
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    n0 = i * (n + 1) * (n + 1) + j * (n + 1) + k
                    n1 = n0 + 1
                    n2 = n0 + (n + 1)
                    n3 = n2 + 1
                    n4 = n0 + (n + 1) * (n + 1)
                    n5 = n4 + 1
                    n6 = n4 + (n + 1)
                    n7 = n6 + 1
                    elements.append([n0, n1, n3, n2, n4, n5, n7, n6])

        elements = np.array(elements)

        return {
            'nodes': nodes,
            'elements': elements,
            'num_nodes': len(nodes),
            'num_elements': len(elements)
        }

    else:
        raise ValueError(f"Unsupported mesh type: {mesh_type}")
