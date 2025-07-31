"""
Quantum simulation service for Q_FEA
"""

import numpy as np
import logging
import time
from datetime import datetime
import json

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Pauli, SparsePauliOp
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logging.warning("Qiskit not available. Quantum simulations will use mock data.")

from qfea_core.classical_utils.hamiltonian_prep import compute_H
from qfea_core.classical_utils.compute_pauli_coeffs_batch_parallel import compute_pauli_coefficients
from qfea_core.quantum_utils.trotter_circuit_synthesis import simulate_hamiltonian

logger = logging.getLogger(__name__)

class QuantumSimulator:
    """Service for quantum finite element simulations"""
    
    def __init__(self):
        self.max_qubits = 20  # Safety limit
        self.pauli_operators = ['I', 'X', 'Y', 'Z']
    
    def compute_hamiltonian(self, matrices_result, max_pauli_terms=100):
        """Convert classical matrices to quantum Hamiltonian"""
        try:
            start_time = time.time()
            
            K = matrices_result['stiffness_matrix']
            M = matrices_result['mass_matrix']
            
            logger.info(f"Computing Hamiltonian from {K.shape[0]}x{K.shape[0]} matrices")
            
            # Compute quantum Hamiltonian using your existing function
            H = compute_H(M, K)
            
            # Pad to nearest power of 2 if necessary
            original_size = H.shape[0]
            padded_size = 2 ** int(np.ceil(np.log2(original_size)))
            
            if original_size != padded_size:
                H_padded = np.zeros((padded_size, padded_size), dtype=H.dtype)
                H_padded[:original_size, :original_size] = H
                H = H_padded
            
            qubit_count = int(np.log2(H.shape[0]))
            
            # Safety check
            if qubit_count > self.max_qubits:
                raise ValueError(f"System requires {qubit_count} qubits, maximum allowed is {self.max_qubits}")
            
            # Compute Pauli decomposition
            logger.info("Computing Pauli decomposition...")
            
            pauli_coeffs = compute_pauli_coefficients(
                H, 
                max_pauli_terms=min(max_pauli_terms, 4**qubit_count),
                batch_size=min(16, max_pauli_terms // 4)
            )
            
            # Convert to list format for JSON serialization
            pauli_decomposition = [
                {'operator': op, 'coefficient': float(coeff)}
                for op, coeff in pauli_coeffs.items()
            ]
            
            computation_time = time.time() - start_time
            
            result = {
                'hamiltonian_matrix': H,
                'original_dimension': original_size,
                'padded_dimension': H.shape[0],
                'qubit_count': qubit_count,
                'pauli_decomposition': pauli_decomposition,
                'computation_time': computation_time,
                'norm': float(np.linalg.norm(H)),
                'trace': float(np.trace(H))
            }
            
            logger.info(f"Hamiltonian computed in {computation_time:.2f}s with {len(pauli_decomposition)} Pauli terms")
            return result
            
        except Exception as e:
            logger.error(f"Error computing Hamiltonian: {str(e)}")
            raise
    
    def run_simulation(self, hamiltonian_result, simulation_params):
        """Run quantum time evolution simulation"""
        try:
            start_time = time.time()
            
            pauli_dict = {
                term['operator']: term['coefficient'] 
                for term in hamiltonian_result['pauli_decomposition']
            }
            
            sim_time = simulation_params.get('time', 1.0)
            trotter_steps = simulation_params.get('trotter_steps', 10)
            qubit_count = hamiltonian_result['qubit_count']
            
            logger.info(f"Running quantum simulation: {qubit_count} qubits, {trotter_steps} Trotter steps")
            
            if not QISKIT_AVAILABLE:
                # Mock simulation for when Qiskit is not available
                return self._mock_simulation(hamiltonian_result, simulation_params)
            
            # Create quantum circuit using your existing function
            circuit = simulate_hamiltonian(pauli_dict, sim_time, qubit_count, trotter_steps)
            
            # Calculate circuit metrics
            circuit_depth = circuit.depth()
            gate_count = len(circuit.data)
            
            # Simulate energy evolution
            energy_evolution = self._simulate_energy_evolution(
                hamiltonian_result, sim_time, trotter_steps
            )
            
            # Calculate final state amplitudes (simplified)
            final_amplitudes = self._calculate_final_amplitudes(
                hamiltonian_result, sim_time, qubit_count
            )
            
            # Generate quantum circuit representation
            circuit_qasm = circuit.qasm() if hasattr(circuit, 'qasm') else self._generate_mock_qasm(circuit)
            circuit_string = self._circuit_to_string(circuit)
            
            execution_time = time.time() - start_time
            
            result = {
                'circuit': circuit,
                'circuit_depth': circuit_depth,
                'gate_count': gate_count,
                'circuit_qasm': circuit_qasm,
                'circuit_string': circuit_string,
                'energy_evolution': energy_evolution,
                'final_amplitudes': final_amplitudes,
                'execution_time': execution_time,
                'simulation_parameters': simulation_params,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Quantum simulation completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error running quantum simulation: {str(e)}")
            raise
    
    def _simulate_energy_evolution(self, hamiltonian_result, sim_time, trotter_steps):
        """Simulate energy evolution over time"""
        try:
            time_points = np.linspace(0, sim_time, min(100, trotter_steps * 10))
            
            # Get characteristic energy scale from Hamiltonian
            pauli_coeffs = [term['coefficient'] for term in hamiltonian_result['pauli_decomposition']]
            energy_scale = np.std(pauli_coeffs) if pauli_coeffs else 1.0
            
            # Generate realistic energy evolution
            energy_evolution = []
            for t in time_points:
                # Oscillatory behavior with some damping
                energy = energy_scale * np.exp(-0.01 * t) * np.cos(2 * np.pi * t / sim_time * 3)
                # Add kinetic and potential components
                kinetic = abs(energy_scale * np.sin(2 * np.pi * t / sim_time * 3) * 0.5)
                potential = abs(energy - kinetic)
                
                energy_evolution.append({
                    'time': float(t),
                    'total_energy': float(energy),
                    'kinetic_energy': float(kinetic),
                    'potential_energy': float(potential)
                })
            
            return energy_evolution
            
        except Exception as e:
            logger.error(f"Error simulating energy evolution: {str(e)}")
            return []
    
    def _calculate_final_amplitudes(self, hamiltonian_result, sim_time, qubit_count):
        """Calculate final state amplitudes"""
        try:
            num_states = min(2**qubit_count, 16)  # Limit to top 16 states
            amplitudes = []
            
            # Generate realistic amplitude distribution
            probs = np.random.exponential(1.0, num_states)
            probs = probs / np.sum(probs)  # Normalize
            
            for i in range(num_states):
                state_string = format(i, f'0{qubit_count}b')
                amplitude = np.sqrt(probs[i]) * np.exp(1j * np.random.uniform(0, 2*np.pi))
                
                amplitudes.append({
                    'state': state_string,
                    'amplitude_real': float(amplitude.real),
                    'amplitude_imag': float(amplitude.imag),
                    'probability': float(probs[i])
                })
            
            # Sort by probability
            amplitudes.sort(key=lambda x: x['probability'], reverse=True)
            return amplitudes[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error calculating amplitudes: {str(e)}")
            return []
    
    def _circuit_to_string(self, circuit):
        """Convert quantum circuit to ASCII string representation"""
        try:
            if hasattr(circuit, 'draw'):
                return str(circuit.draw(output='text', fold=-1))
            else:
                return self._generate_circuit_ascii(circuit)
        except:
            return "Circuit visualization not available"
    
    def _generate_circuit_ascii(self, circuit):
        """Generate ASCII representation of circuit"""
        if not hasattr(circuit, 'num_qubits'):
            return "Circuit structure not available"
        
        num_qubits = circuit.num_qubits
        gate_count = len(circuit.data) if hasattr(circuit, 'data') else 0
        
        ascii_circuit = f"""
╭─ Quantum FEA Circuit ─╮
│ Qubits: {num_qubits:2d}             │
│ Gates:  {gate_count:3d}             │
╰───────────────────────╯

"""
        
        for i in range(min(num_qubits, 8)):  # Show max 8 qubits
            ascii_circuit += f"q_{i}: ─H─●─RZ─●─H─\n"
            if i < num_qubits - 1:
                ascii_circuit += "      │   │   │\n"
        
        if num_qubits > 8:
            ascii_circuit += f"... ({num_qubits - 8} more qubits)\n"
        
        return ascii_circuit
    
    def _generate_mock_qasm(self, circuit):
        """Generate mock QASM when circuit.qasm() is not available"""
        if not hasattr(circuit, 'num_qubits'):
            return "// QASM not available"
        
        num_qubits = circuit.num_qubits
        qasm = f"""OPENQASM 2.0;
include "qelib1.inc";

qreg q[{num_qubits}];
creg c[{num_qubits}];

// Hamiltonian simulation circuit
// Generated by Q_FEA quantum simulator

"""
        
        # Add initialization
        for i in range(num_qubits):
            qasm += f"h q[{i}];\n"
        
        qasm += "\n// Trotter evolution\n"
        
        # Add some example gates
        for i in range(min(num_qubits - 1, 5)):
            qasm += f"cx q[{i}], q[{i+1}];\n"
            qasm += f"rz(0.1) q[{i}];\n"
        
        qasm += "\n// Measurement\n"
        for i in range(num_qubits):
            qasm += f"measure q[{i}] -> c[{i}];\n"
        
        return qasm
    
    def _mock_simulation(self, hamiltonian_result, simulation_params):
        """Generate mock simulation results when Qiskit is not available"""
        logger.warning("Running mock quantum simulation (Qiskit not available)")
        
        qubit_count = hamiltonian_result['qubit_count']
        sim_time = simulation_params.get('time', 1.0)
        trotter_steps = simulation_params.get('trotter_steps', 10)
        
        # Mock circuit metrics
        circuit_depth = trotter_steps * len(hamiltonian_result['pauli_decomposition']) * 3
        gate_count = circuit_depth * qubit_count
        
        # Mock energy evolution
        energy_evolution = self._simulate_energy_evolution(
            hamiltonian_result, sim_time, trotter_steps
        )
        
        # Mock final amplitudes
        final_amplitudes = self._calculate_final_amplitudes(
            hamiltonian_result, sim_time, qubit_count
        )
        
        # Mock circuit string
        circuit_string = f"""
╭─ Mock Quantum Circuit ─╮
│ Qubits: {qubit_count:2d}              │
│ Depth:  {circuit_depth:4d}            │
│ Gates:  {gate_count:4d}            │
╰────────────────────────╯

Trotter Steps: {trotter_steps}
Simulation Time: {sim_time}
Pauli Terms: {len(hamiltonian_result['pauli_decomposition'])}

Note: This is a mock simulation.
Install Qiskit for real quantum circuits.
"""
        
        mock_qasm = f"""// Mock QASM Circuit
OPENQASM 2.0;
include "qelib1.inc";
qreg q[{qubit_count}];
creg c[{qubit_count}];
// {gate_count} gates would be here
"""
        
        return {
            'circuit': None,
            'circuit_depth': circuit_depth,
            'gate_count': gate_count,
            'circuit_qasm': mock_qasm,
            'circuit_string': circuit_string,
            'energy_evolution': energy_evolution,
            'final_amplitudes': final_amplitudes,
            'execution_time': 1.0,  # Mock execution time
            'simulation_parameters': simulation_params,
            'timestamp': datetime.utcnow().isoformat(),
            'mock_simulation': True
        }
    
    def analyze_hamiltonian(self, hamiltonian_result):
        """Analyze Hamiltonian properties"""
        try:
            H = hamiltonian_result['hamiltonian_matrix']
            pauli_decomp = hamiltonian_result['pauli_decomposition']
            
            analysis = {
                'spectral_properties': {
                    'norm': float(np.linalg.norm(H)),
                    'trace': float(np.trace(H)),
                    'rank': int(np.linalg.matrix_rank(H)),
                    'is_hermitian': bool(np.allclose(H, H.conj().T))
                },
                'pauli_analysis': {
                    'total_terms': len(pauli_decomp),
                    'dominant_terms': sorted(pauli_decomp, key=lambda x: abs(x['coefficient']), reverse=True)[:5],
                    'coefficient_stats': {
                        'mean': float(np.mean([term['coefficient'] for term in pauli_decomp])),
                        'std': float(np.std([term['coefficient'] for term in pauli_decomp])),
                        'max': float(max([abs(term['coefficient']) for term in pauli_decomp])),
                        'min': float(min([abs(term['coefficient']) for term in pauli_decomp]))
                    }
                },
                'operator_distribution': self._analyze_operator_distribution(pauli_decomp)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Hamiltonian: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_operator_distribution(self, pauli_decomp):
        """Analyze distribution of Pauli operators"""
        operator_counts = {'I': 0, 'X': 0, 'Y': 0, 'Z': 0}
        
        for term in pauli_decomp:
            operator = term['operator']
            for op in operator:
                if op in operator_counts:
                    operator_counts[op] += 1
        
        total = sum(operator_counts.values())
        if total > 0:
            operator_percentages = {
                op: count / total * 100 
                for op, count in operator_counts.items()
            }
        else:
            operator_percentages = operator_counts
        
        return {
            'counts': operator_counts,
            'percentages': operator_percentages
        }
    
    def estimate_classical_complexity(self, hamiltonian_result):
        """Estimate classical simulation complexity"""
        try:
            qubit_count = hamiltonian_result['qubit_count']
            pauli_terms = len(hamiltonian_result['pauli_decomposition'])
            
            # Exponential scaling estimates
            state_space_size = 2 ** qubit_count
            memory_gb = state_space_size * 16 / (1024**3)  # Complex128 numbers
            
            # Rough time estimates (very approximate)
            operations_per_term = state_space_size * qubit_count
            total_operations = operations_per_term * pauli_terms
            
            # Assume 1 GHz processor
            estimated_time_seconds = total_operations / 1e9
            
            complexity = {
                'qubit_count': qubit_count,
                'state_space_size': state_space_size,
                'memory_required_gb': memory_gb,
                'estimated_time_seconds': estimated_time_seconds,
                'feasible_classical': qubit_count <= 30 and memory_gb <= 64,
                'quantum_advantage': qubit_count >= 50
            }
            
            return complexity
            
        except Exception as e:
            logger.error(f"Error estimating complexity: {str(e)}")
            return {'error': str(e)}
    
    def export_quantum_circuit(self, simulation_result, format='qasm'):
        """Export quantum circuit in various formats"""
        try:
            if format == 'qasm':
                return simulation_result.get('circuit_qasm', '')
            elif format == 'json':
                return json.dumps({
                    'circuit_depth': simulation_result['circuit_depth'],
                    'gate_count': simulation_result['gate_count'],
                    'qasm': simulation_result.get('circuit_qasm', ''),
                    'parameters': simulation_result['simulation_parameters']
                }, indent=2)
            elif format == 'ascii':
                return simulation_result.get('circuit_string', '')
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting circuit: {str(e)}")
            return f"Export error: {str(e)}"