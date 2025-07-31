"""
API routes for Q_FEA Web Application
"""

import os
import uuid
import logging
from pathlib import Path
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import numpy as np

from app.services.mesh_processor import MeshProcessor
from app.services.quantum_simulator import QuantumSimulator
from app.services.file_handler import FileHandler
from app.api.utils import allowed_file, validate_material_properties, create_response

# Create blueprint
api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize services
mesh_processor = MeshProcessor()
quantum_simulator = QuantumSimulator()
file_handler = FileHandler()

@api_bp.route('/upload', methods=['POST'])
def upload_mesh():
    """Upload and process mesh file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return create_response(False, 'No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return create_response(False, 'No file selected', 400)
        
        # Validate file
        if not allowed_file(file.filename):
            return create_response(False, 'File type not allowed', 400)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        unique_filename = f"{unique_id}{file_extension}"
        
        # Save file
        file_path = current_app.config['UPLOAD_FOLDER'] / unique_filename
        file.save(file_path)
        
        logger.info(f"File uploaded: {filename} -> {unique_filename}")
        
        # Process mesh metadata
        try:
            mesh_info = mesh_processor.get_mesh_info(file_path)
            
            # Store file metadata
            file_handler.store_file_metadata(unique_id, {
                'original_filename': filename,
                'unique_filename': unique_filename,
                'file_path': str(file_path),
                'upload_time': datetime.utcnow().isoformat(),
                'mesh_info': mesh_info
            })
            
            return create_response(True, 'File uploaded successfully', 200, {
                'file_id': unique_id,
                'mesh_info': mesh_info
            })
            
        except Exception as e:
            # Clean up file if processing fails
            if file_path.exists():
                file_path.unlink()
            raise e
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return create_response(False, f'Upload failed: {str(e)}', 500)

@api_bp.route('/process_matrices', methods=['POST'])
def process_matrices():
    """Compute stiffness and mass matrices"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        material_properties = data.get('material_properties', {})
        
        # Validate inputs
        if not file_id:
            return create_response(False, 'File ID required', 400)
        
        if not validate_material_properties(material_properties):
            return create_response(False, 'Invalid material properties', 400)
        
        # Get file metadata
        file_metadata = file_handler.get_file_metadata(file_id)
        if not file_metadata:
            return create_response(False, 'File not found', 404)
        
        file_path = Path(file_metadata['file_path'])
        if not file_path.exists():
            return create_response(False, 'File not found on disk', 404)
        
        # Process matrices
        logger.info(f"Computing matrices for file_id: {file_id}")
        
        matrices_result = mesh_processor.compute_matrices(
            file_path, 
            material_properties
        )
        
        # Store results
        file_handler.store_computation_result(file_id, 'matrices', matrices_result)
        
        return create_response(True, 'Matrices computed successfully', 200, {
            'matrices': {
                'dimension': matrices_result['dimension'],
                'dof_count': matrices_result['dof_count'],
                'condition_number': matrices_result['condition_number'],
                'sparsity': matrices_result['sparsity']
            }
        })
        
    except Exception as e:
        logger.error(f"Matrix computation error: {str(e)}")
        return create_response(False, f'Matrix computation failed: {str(e)}', 500)

@api_bp.route('/compute_hamiltonian', methods=['POST'])
def compute_hamiltonian():
    """Convert matrices to quantum Hamiltonian"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        max_pauli_terms = data.get('max_pauli_terms', current_app.config['MAX_PAULI_TERMS'])
        
        if not file_id:
            return create_response(False, 'File ID required', 400)
        
        # Get matrices result
        matrices_result = file_handler.get_computation_result(file_id, 'matrices')
        if not matrices_result:
            return create_response(False, 'Matrices not computed yet', 400)
        
        logger.info(f"Computing Hamiltonian for file_id: {file_id}")
        
        # Compute Hamiltonian
        hamiltonian_result = quantum_simulator.compute_hamiltonian(
            matrices_result, 
            max_pauli_terms
        )
        
        # Store results
        file_handler.store_computation_result(file_id, 'hamiltonian', hamiltonian_result)
        
        return create_response(True, 'Hamiltonian computed successfully', 200, {
            'hamiltonian': {
                'pauli_terms': len(hamiltonian_result['pauli_decomposition']),
                'qubit_count': hamiltonian_result['qubit_count'],
                'pauli_decomposition': hamiltonian_result['pauli_decomposition'][:20]  # Return first 20 terms
            }
        })
        
    except Exception as e:
        logger.error(f"Hamiltonian computation error: {str(e)}")
        return create_response(False, f'Hamiltonian computation failed: {str(e)}', 500)

@api_bp.route('/run_simulation', methods=['POST'])
def run_simulation():
    """Run quantum simulation"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        simulation_params = data.get('simulation_params', {})
        
        if not file_id:
            return create_response(False, 'File ID required', 400)
        
        # Get Hamiltonian result
        hamiltonian_result = file_handler.get_computation_result(file_id, 'hamiltonian')
        if not hamiltonian_result:
            return create_response(False, 'Hamiltonian not computed yet', 400)
        
        # Validate simulation parameters
        sim_time = simulation_params.get('time', 1.0)
        trotter_steps = simulation_params.get('trotter_steps', current_app.config['DEFAULT_TROTTER_STEPS'])
        
        if sim_time <= 0 or trotter_steps <= 0:
            return create_response(False, 'Invalid simulation parameters', 400)
        
        logger.info(f"Running quantum simulation for file_id: {file_id}")
        
        # Run simulation
        simulation_result = quantum_simulator.run_simulation(
            hamiltonian_result,
            simulation_params
        )
        
        # Store results
        file_handler.store_computation_result(file_id, 'simulation', simulation_result)
        
        return create_response(True, 'Simulation completed successfully', 200, {
            'simulation': {
                'circuit_depth': simulation_result['circuit_depth'],
                'gate_count': simulation_result['gate_count'],
                'execution_time': simulation_result['execution_time'],
                'energy_evolution': simulation_result['energy_evolution'][-100:],  # Last 100 points
                'final_amplitudes': simulation_result['final_amplitudes'][:10]  # Top 10 states
            }
        })
        
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        return create_response(False, f'Simulation failed: {str(e)}', 500)

@api_bp.route('/get_results/<file_id>', methods=['GET'])
def get_results(file_id):
    """Get all computation results for a file"""
    try:
        if not file_id:
            return create_response(False, 'File ID required', 400)
        
        # Get all results
        file_metadata = file_handler.get_file_metadata(file_id)
        matrices_result = file_handler.get_computation_result(file_id, 'matrices')
        hamiltonian_result = file_handler.get_computation_result(file_id, 'hamiltonian')
        simulation_result = file_handler.get_computation_result(file_id, 'simulation')
        
        if not file_metadata:
            return create_response(False, 'File not found', 404)
        
        results = {
            'file_info': {
                'original_filename': file_metadata['original_filename'],
                'upload_time': file_metadata['upload_time'],
                'mesh_info': file_metadata['mesh_info']
            }
        }
        
        if matrices_result:
            results['matrices'] = {
                'dimension': matrices_result['dimension'],
                'dof_count': matrices_result['dof_count'],
                'condition_number': matrices_result['condition_number'],
                'sparsity': matrices_result['sparsity']
            }
        
        if hamiltonian_result:
            results['hamiltonian'] = {
                'pauli_terms': len(hamiltonian_result['pauli_decomposition']),
                'qubit_count': hamiltonian_result['qubit_count'],
                'pauli_decomposition': hamiltonian_result['pauli_decomposition']
            }
        
        if simulation_result:
            results['simulation'] = {
                'circuit_depth': simulation_result['circuit_depth'],
                'gate_count': simulation_result['gate_count'],
                'execution_time': simulation_result['execution_time'],
                'energy_evolution': simulation_result['energy_evolution'],
                'final_amplitudes': simulation_result['final_amplitudes']
            }
        
        return create_response(True, 'Results retrieved successfully', 200, results)
        
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return create_response(False, f'Failed to retrieve results: {str(e)}', 500)

@api_bp.route('/export/<file_id>/<format>', methods=['GET'])
def export_results(file_id, format):
    """Export results in various formats"""
    try:
        if format not in ['json', 'csv', 'qasm']:
            return create_response(False, 'Invalid export format', 400)
        
        # Get all results
        results = get_results(file_id)
        if not results.get_json().get('success'):
            return results
        
        data = results.get_json()['data']
        
        # Generate export file
        export_path = file_handler.export_results(file_id, data, format)
        
        return send_file(
            export_path,
            as_attachment=True,
            download_name=f"qfea_results_{file_id}.{format}"
        )
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return create_response(False, f'Export failed: {str(e)}', 500)

@api_bp.route('/material_presets', methods=['GET'])
def get_material_presets():
    """Get available material presets"""
    try:
        presets = current_app.config['MATERIAL_PRESETS']
        return create_response(True, 'Material presets retrieved', 200, presets)
        
    except Exception as e:
        logger.error(f"Material presets error: {str(e)}")
        return create_response(False, f'Failed to get presets: {str(e)}', 500)

@api_bp.route('/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Get processing status for a file"""
    try:
        status = file_handler.get_processing_status(file_id)
        return create_response(True, 'Status retrieved', 200, status)
        
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return create_response(False, f'Failed to get status: {str(e)}', 500)

@api_bp.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete file and all associated data"""
    try:
        success = file_handler.delete_file_data(file_id)
        if success:
            return create_response(True, 'File deleted successfully', 200)
        else:
            return create_response(False, 'File not found', 404)
            
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return create_response(False, f'Delete failed: {str(e)}', 500)

# Error handlers for the blueprint
@api_bp.errorhandler(413)
def file_too_large(error):
    return create_response(False, 'File too large', 413)

@api_bp.errorhandler(400)
def bad_request(error):
    return create_response(False, 'Bad request', 400)

@api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f'API Internal Error: {error}')
    return create_response(False, 'Internal server error', 500)