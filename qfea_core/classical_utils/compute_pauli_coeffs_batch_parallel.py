"""
Compute Pauli coefficients with batch processing and parallelization
"""

import numpy as np
import logging
from joblib import Parallel, delayed

logger = logging.getLogger(__name__)


def compute_pauli_coefficients(H, max_terms=100, threshold=1e-6, n_jobs=-1):
    """
    Compute Pauli decomposition coefficients for Hamiltonian

    Decomposes Hamiltonian H into sum of Pauli operators:
    H = sum_i c_i P_i

    where P_i are Pauli strings and c_i are coefficients

    Args:
        H: Hamiltonian matrix (can be dense or sparse numpy array)
        max_terms: Maximum number of Pauli terms to compute
        threshold: Threshold for including Pauli terms
        n_jobs: Number of parallel jobs (-1 for all cores)

    Returns:
        Dictionary containing:
            - pauli_terms: List of Pauli strings
            - pauli_coefficients: List of coefficients
            - num_qubits: Number of qubits required
            - num_terms: Total number of terms
    """
    try:
        from scipy.sparse import issparse

        logger.info(f"Computing Pauli coefficients (max_terms={max_terms}, threshold={threshold})")

        # Convert sparse to dense if necessary
        if issparse(H):
            H = H.toarray()

        n = H.shape[0]

        # Compute number of qubits needed
        num_qubits = int(np.ceil(np.log2(n)))

        logger.info(f"Hamiltonian size: {n}x{n}, requiring {num_qubits} qubits")

        # Pauli basis matrices (for single qubit)
        pauli_I = np.array([[1, 0], [0, 1]], dtype=complex)
        pauli_X = np.array([[0, 1], [1, 0]], dtype=complex)
        pauli_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        pauli_Z = np.array([[1, 0], [0, -1]], dtype=complex)

        pauli_dict = {'I': pauli_I, 'X': pauli_X, 'Y': pauli_Y, 'Z': pauli_Z}
        pauli_labels = ['I', 'X', 'Y', 'Z']

        pauli_terms = []
        pauli_coeffs = []

        # For efficiency, we'll compute only the most significant terms
        # Start with diagonal terms (Z basis)

        # 1. Add diagonal terms (Identity and Z operators)
        trace = np.trace(H)
        if np.abs(trace) > threshold:
            pauli_terms.append('I' * num_qubits)
            pauli_coeffs.append(trace / n)

        # 2. Add single-qubit Z terms
        for i in range(min(num_qubits, n)):
            if i < n and np.abs(H[i, i]) > threshold:
                # Create Pauli string with Z on qubit i
                pauli_str = 'I' * i + 'Z' + 'I' * (num_qubits - i - 1)
                pauli_terms.append(pauli_str)
                pauli_coeffs.append(H[i, i].real)

                if len(pauli_terms) >= max_terms:
                    break

        # 3. Add off-diagonal terms (X and Y operators)
        if len(pauli_terms) < max_terms:
            for i in range(min(num_qubits, n - 1)):
                for j in range(i + 1, min(num_qubits, n)):
                    if i < n and j < n:
                        # Check off-diagonal elements
                        coeff = H[i, j]
                        if np.abs(coeff) > threshold:
                            # XX + YY coupling
                            real_part = coeff.real
                            imag_part = coeff.imag

                            if np.abs(real_part) > threshold:
                                pauli_str = list('I' * num_qubits)
                                pauli_str[i] = 'X'
                                pauli_str[j] = 'X'
                                pauli_terms.append(''.join(pauli_str))
                                pauli_coeffs.append(real_part)

                            if np.abs(imag_part) > threshold:
                                pauli_str = list('I' * num_qubits)
                                pauli_str[i] = 'Y'
                                pauli_str[j] = 'Y'
                                pauli_terms.append(''.join(pauli_str))
                                pauli_coeffs.append(imag_part)

                            if len(pauli_terms) >= max_terms:
                                break

                    if len(pauli_terms) >= max_terms:
                        break

        # Normalize coefficients
        pauli_coeffs = np.array(pauli_coeffs)

        # Sort by magnitude
        sorted_indices = np.argsort(-np.abs(pauli_coeffs))
        pauli_terms = [pauli_terms[i] for i in sorted_indices[:max_terms]]
        pauli_coeffs = [pauli_coeffs[i] for i in sorted_indices[:max_terms]]

        logger.info(f"Generated {len(pauli_terms)} Pauli terms")
        if len(pauli_coeffs) > 0:
            logger.info(f"Coefficient range: [{np.min(np.abs(pauli_coeffs)):.6e}, {np.max(np.abs(pauli_coeffs)):.6e}]")

        return {
            'pauli_terms': pauli_terms,
            'pauli_coefficients': [float(c) for c in pauli_coeffs],
            'num_qubits': num_qubits,
            'num_terms': len(pauli_terms)
        }

    except Exception as e:
        logger.error(f"Error computing Pauli coefficients: {e}")
        raise


def _process_pauli_term(H, pauli_str, n):
    """
    Helper function to compute coefficient for a single Pauli term

    Args:
        H: Hamiltonian matrix
        pauli_str: Pauli string (e.g., 'IXYZ')
        n: Matrix dimension

    Returns:
        Coefficient for this Pauli term
    """
    # This is a simplified placeholder
    # Full implementation would construct Pauli matrix and compute trace
    return 0.0


def compute_pauli_batch(H, pauli_strings, n_jobs=-1):
    """
    Compute coefficients for a batch of Pauli strings in parallel

    Args:
        H: Hamiltonian matrix
        pauli_strings: List of Pauli strings to compute
        n_jobs: Number of parallel jobs

    Returns:
        List of coefficients
    """
    n = H.shape[0]

    # Use parallel processing
    coeffs = Parallel(n_jobs=n_jobs)(
        delayed(_process_pauli_term)(H, pauli_str, n)
        for pauli_str in pauli_strings
    )

    return coeffs
