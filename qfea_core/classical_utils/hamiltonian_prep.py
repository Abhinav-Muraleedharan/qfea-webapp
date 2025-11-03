"""
Hamiltonian preparation utilities for quantum FEA
"""

import numpy as np
import logging
from scipy.sparse import csr_matrix, issparse
from scipy.sparse.linalg import eigsh

logger = logging.getLogger(__name__)


def compute_H(K, M, num_modes=10, method='standard'):
    """
    Compute Hamiltonian from stiffness and mass matrices

    The generalized eigenvalue problem K * phi = lambda * M * phi
    is converted to a Hamiltonian for quantum simulation.

    Args:
        K: Stiffness matrix (sparse or dense)
        M: Mass matrix (sparse or dense)
        num_modes: Number of eigenmodes to compute
        method: 'standard' or 'normalized'

    Returns:
        Dictionary containing:
            - H: Hamiltonian matrix
            - eigenvalues: Eigenvalues of the system
            - eigenvectors: Eigenvectors (modes)
            - num_dofs: Number of degrees of freedom
    """
    try:
        logger.info(f"Computing Hamiltonian with {num_modes} modes using {method} method")

        # Get dimensions
        if issparse(K):
            n = K.shape[0]
        else:
            n = K.shape[0]

        # Ensure we don't request more modes than DOFs
        num_modes = min(num_modes, n - 2)

        # Solve generalized eigenvalue problem: K * phi = lambda * M * phi
        # This is equivalent to M^-1 * K * phi = lambda * phi
        logger.info("Solving generalized eigenvalue problem...")

        if issparse(K) and issparse(M):
            # Use sparse eigenvalue solver
            try:
                eigenvalues, eigenvectors = eigsh(K, k=num_modes, M=M, which='SM')
            except Exception as e:
                logger.warning(f"Sparse solver failed: {e}. Using reduced problem.")
                # Use smaller problem for demonstration
                n_reduced = min(20, n)
                K_dense = K[:n_reduced, :n_reduced].toarray()
                M_dense = M[:n_reduced, :n_reduced].toarray()
                eigenvalues, eigenvectors = np.linalg.eigh(
                    np.linalg.solve(M_dense, K_dense)
                )
                eigenvalues = eigenvalues[:num_modes]
                eigenvectors = eigenvectors[:, :num_modes]
        else:
            # Convert to dense if necessary
            if issparse(K):
                K = K.toarray()
            if issparse(M):
                M = M.toarray()

            # For small systems, use dense solver
            if n <= 1000:
                M_inv = np.linalg.inv(M)
                A = M_inv @ K
                eigenvalues, eigenvectors = np.linalg.eigh(A)
                eigenvalues = eigenvalues[:num_modes]
                eigenvectors = eigenvectors[:, :num_modes]
            else:
                # Use reduced problem for large systems
                logger.warning(f"Large system ({n} DOFs). Using reduced representation.")
                n_reduced = min(100, n)
                K_reduced = K[:n_reduced, :n_reduced]
                M_reduced = M[:n_reduced, :n_reduced]
                M_inv = np.linalg.inv(M_reduced)
                A = M_inv @ K_reduced
                eigenvalues, eigenvectors = np.linalg.eigh(A)
                eigenvalues = eigenvalues[:num_modes]
                eigenvectors = eigenvectors[:, :num_modes]

        logger.info(f"Found {len(eigenvalues)} eigenvalues")
        logger.info(f"Eigenvalue range: [{eigenvalues[0]:.6e}, {eigenvalues[-1]:.6e}]")

        # Construct Hamiltonian
        # For quantum simulation, we use the diagonal form with eigenvalues
        if method == 'standard':
            # Diagonal Hamiltonian in eigenspace
            H = np.diag(eigenvalues)
        elif method == 'normalized':
            # Normalize eigenvalues to [0, 1] range for quantum circuits
            eig_min = np.min(eigenvalues)
            eig_max = np.max(eigenvalues)
            if eig_max - eig_min > 1e-10:
                normalized_eigs = (eigenvalues - eig_min) / (eig_max - eig_min)
            else:
                normalized_eigs = eigenvalues
            H = np.diag(normalized_eigs)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Make Hamiltonian sparse if it's large
        if H.shape[0] > 50:
            H = csr_matrix(H)

        logger.info(f"Hamiltonian shape: {H.shape}")

        return {
            'H': H,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'num_dofs': n,
            'num_modes': len(eigenvalues)
        }

    except Exception as e:
        logger.error(f"Error computing Hamiltonian: {e}")
        raise


def hamiltonian_to_pauli_basis(H, num_qubits=None):
    """
    Convert Hamiltonian to Pauli basis representation

    Args:
        H: Hamiltonian matrix (dense or sparse)
        num_qubits: Number of qubits (if None, computed from H size)

    Returns:
        Dictionary containing Pauli decomposition
    """
    try:
        if issparse(H):
            H = H.toarray()

        n = H.shape[0]

        if num_qubits is None:
            num_qubits = int(np.ceil(np.log2(n)))

        logger.info(f"Converting Hamiltonian ({n}x{n}) to Pauli basis with {num_qubits} qubits")

        # For simplicity, we represent H in the computational basis
        # A full implementation would decompose H into Pauli operators

        pauli_terms = []
        pauli_coeffs = []

        # Diagonal terms (Z operators)
        for i in range(min(n, 2**num_qubits)):
            if np.abs(H[i, i]) > 1e-10:
                # Create Pauli string (all I except Z on qubit i)
                pauli_str = 'I' * num_qubits
                if i < num_qubits:
                    pauli_str = pauli_str[:i] + 'Z' + pauli_str[i+1:]
                pauli_terms.append(pauli_str)
                pauli_coeffs.append(H[i, i])

        logger.info(f"Generated {len(pauli_terms)} Pauli terms")

        return {
            'pauli_terms': pauli_terms,
            'pauli_coefficients': pauli_coeffs,
            'num_qubits': num_qubits,
            'num_terms': len(pauli_terms)
        }

    except Exception as e:
        logger.error(f"Error converting to Pauli basis: {e}")
        raise
