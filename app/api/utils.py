"""
Utility functions for API routes
"""

from flask import current_app, jsonify
from pathlib import Path

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_material_properties(properties):
    """Validate material properties"""
    required_fields = ['young_modulus', 'poisson_ratio', 'density']
    
    if not isinstance(properties, dict):
        return False
    
    for field in required_fields:
        if field not in properties:
            return False
        
        value = properties[field]
        if not isinstance(value, (int, float)) or value <= 0:
            return False
    
    # Validate Poisson's ratio range
    poisson = properties['poisson_ratio']
    if not (0 < poisson < 0.5):
        return False
    
    return True

def create_response(success, message, status_code, data=None):
    """Create standardized API response"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return Path(file_path).stat().st_size
    except:
        return 0

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_simulation_parameters(params):
    """Validate quantum simulation parameters"""
    if not isinstance(params, dict):
        return False, "Parameters must be a dictionary"
    
    # Check simulation time
    sim_time = params.get('time', 1.0)
    if not isinstance(sim_time, (int, float)) or sim_time <= 0:
        return False, "Simulation time must be positive"
    
    # Check Trotter steps
    trotter_steps = params.get('trotter_steps', 10)
    if not isinstance(trotter_steps, int) or trotter_steps <= 0:
        return False, "Trotter steps must be positive integer"
    
    # Check max Pauli terms
    max_pauli = params.get('max_pauli_terms', 100)
    if not isinstance(max_pauli, int) or max_pauli <= 0:
        return False, "Max Pauli terms must be positive integer"
    
    # Check against limits
    if trotter_steps > 1000:
        return False, "Trotter steps cannot exceed 1000"
    
    if max_pauli > current_app.config['MAX_PAULI_TERMS']:
        return False, f"Max Pauli terms cannot exceed {current_app.config['MAX_PAULI_TERMS']}"
    
    return True, "Valid parameters"

from datetime import datetime