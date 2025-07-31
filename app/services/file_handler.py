"""
File handling service for Q_FEA
"""

import os
import json
import pickle
import logging
import csv
from pathlib import Path
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class FileHandler:
    """Service for handling file operations and metadata storage"""
    
    def __init__(self):
        self.metadata_dir = Path('temp/metadata')
        self.results_dir = Path('temp/results')
        self.exports_dir = Path('temp/exports')
        
        # Create directories
        for directory in [self.metadata_dir, self.results_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def store_file_metadata(self, file_id, metadata):
        """Store metadata for uploaded file"""
        try:
            metadata_file = self.metadata_dir / f"{file_id}.json"
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Metadata stored for file_id: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing metadata: {str(e)}")
            return False
    
    def get_file_metadata(self, file_id):
        """Retrieve metadata for a file"""
        try:
            metadata_file = self.metadata_dir / f"{file_id}.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error retrieving metadata: {str(e)}")
            return None
    
    def store_computation_result(self, file_id, computation_type, result):
        """Store computation results"""
        try:
            result_file = self.results_dir / f"{file_id}_{computation_type}.pkl"
            
            # Store using pickle for complex objects
            with open(result_file, 'wb') as f:
                pickle.dump(result, f)
            
            # Also store a JSON summary for easier access
            summary_file = self.results_dir / f"{file_id}_{computation_type}_summary.json"
            summary = self._create_result_summary(result, computation_type)
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Results stored for file_id: {file_id}, type: {computation_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing results: {str(e)}")
            return False
    
    def get_computation_result(self, file_id, computation_type):
        """Retrieve computation results"""
        try:
            result_file = self.results_dir / f"{file_id}_{computation_type}.pkl"
            
            if not result_file.exists():
                return None
            
            with open(result_file, 'rb') as f:
                result = pickle.load(f)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving results: {str(e)}")
            return None
    
    def get_processing_status(self, file_id):
        """Get current processing status for a file"""
        try:
            status = {
                'file_id': file_id,
                'uploaded': False,
                'matrices_computed': False,
                'hamiltonian_computed': False,
                'simulation_completed': False,
                'last_updated': None
            }
            
            # Check metadata
            metadata = self.get_file_metadata(file_id)
            if metadata:
                status['uploaded'] = True
                status['last_updated'] = metadata.get('upload_time')
            
            # Check computation results
            for comp_type, status_key in [
                ('matrices', 'matrices_computed'),
                ('hamiltonian', 'hamiltonian_computed'),
                ('simulation', 'simulation_completed')
            ]:
                summary_file = self.results_dir / f"{file_id}_{comp_type}_summary.json"
                if summary_file.exists():
                    status[status_key] = True
                    # Update last_updated time
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                        if 'timestamp' in summary:
                            status['last_updated'] = summary['timestamp']
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {'error': str(e)}
    
    def export_results(self, file_id, data, format='json'):
        """Export results in specified format"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            if format == 'json':
                export_file = self.exports_dir / f"qfea_results_{file_id}_{timestamp}.json"
                with open(export_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
            elif format == 'csv':
                export_file = self.exports_dir / f"qfea_results_{file_id}_{timestamp}.csv"
                self._export_to_csv(data, export_file)
                
            elif format == 'qasm':
                export_file = self.exports_dir / f"qfea_circuit_{file_id}_{timestamp}.qasm"
                qasm_content = self._extract_qasm_from_data(data)
                with open(export_file, 'w') as f:
                    f.write(qasm_content)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Results exported to: {export_file}")
            return export_file
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            raise
    
    def delete_file_data(self, file_id):
        """Delete all data associated with a file"""
        try:
            deleted_files = []
            
            # Delete metadata
            metadata_file = self.metadata_dir / f"{file_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
                deleted_files.append(str(metadata_file))
            
            # Delete computation results
            for comp_type in ['matrices', 'hamiltonian', 'simulation']:
                result_file = self.results_dir / f"{file_id}_{comp_type}.pkl"
                summary_file = self.results_dir / f"{file_id}_{comp_type}_summary.json"
                
                for file_path in [result_file, summary_file]:
                    if file_path.exists():
                        file_path.unlink()
                        deleted_files.append(str(file_path))
            
            # Delete uploaded file
            metadata = self.get_file_metadata(file_id)
            if metadata and 'file_path' in metadata:
                uploaded_file = Path(metadata['file_path'])
                if uploaded_file.exists():
                    uploaded_file.unlink()
                    deleted_files.append(str(uploaded_file))
            
            # Delete export files
            for export_file in self.exports_dir.glob(f"*{file_id}*"):
                export_file.unlink()
                deleted_files.append(str(export_file))
            
            logger.info(f"Deleted {len(deleted_files)} files for file_id: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file data: {str(e)}")
            return False
    
    def cleanup_old_files(self, days_old=7):
        """Clean up old files and results"""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
            deleted_count = 0
            
            # Clean up temp directories
            for directory in [self.metadata_dir, self.results_dir, self.exports_dir]:
                for file_path in directory.glob("*"):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return 0
    
    def get_storage_usage(self):
        """Get current storage usage statistics"""
        try:
            usage = {
                'uploads': 0,
                'metadata': 0,
                'results': 0,
                'exports': 0,
                'total': 0
            }
            
            # Calculate upload directory size
            upload_dir = Path('app/static/uploads')
            if upload_dir.exists():
                usage['uploads'] = sum(f.stat().st_size for f in upload_dir.rglob('*') if f.is_file())
            
            # Calculate temp directories
            for dir_name, directory in [
                ('metadata', self.metadata_dir),
                ('results', self.results_dir),
                ('exports', self.exports_dir)
            ]:
                if directory.exists():
                    usage[dir_name] = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            
            usage['total'] = sum(usage.values())
            
            # Convert to human readable format
            for key in usage:
                usage[key] = self._format_bytes(usage[key])
            
            return usage
            
        except Exception as e:
            logger.error(f"Error getting storage usage: {str(e)}")
            return {'error': str(e)}
    
    def _create_result_summary(self, result, computation_type):
        """Create JSON-serializable summary of results"""
        try:
            summary = {
                'computation_type': computation_type,
                'timestamp': datetime.utcnow().isoformat(),
                'success': True
            }
            
            if computation_type == 'matrices':
                summary.update({
                    'dimension': result.get('dimension'),
                    'dof_count': result.get('dof_count'),
                    'condition_number': result.get('condition_number'),
                    'sparsity': result.get('sparsity'),
                    'computation_time': result.get('computation_time')
                })
                
            elif computation_type == 'hamiltonian':
                summary.update({
                    'qubit_count': result.get('qubit_count'),
                    'pauli_terms': len(result.get('pauli_decomposition', [])),
                    'computation_time': result.get('computation_time'),
                    'hamiltonian_norm': result.get('norm')
                })
                
            elif computation_type == 'simulation':
                summary.update({
                    'circuit_depth': result.get('circuit_depth'),
                    'gate_count': result.get('gate_count'),
                    'execution_time': result.get('execution_time'),
                    'energy_points': len(result.get('energy_evolution', [])),
                    'final_states': len(result.get('final_amplitudes', []))
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating result summary: {str(e)}")
            return {
                'computation_type': computation_type,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def _export_to_csv(self, data, file_path):
        """Export data to CSV format"""
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Category', 'Parameter', 'Value'])
            
            # Write file info
            if 'file_info' in data:
                for key, value in data['file_info'].items():
                    writer.writerow(['File Info', key, value])
            
            # Write matrices info
            if 'matrices' in data:
                for key, value in data['matrices'].items():
                    writer.writerow(['Matrices', key, value])
            
            # Write Hamiltonian info
            if 'hamiltonian' in data:
                hamiltonian = data['hamiltonian']
                for key, value in hamiltonian.items():
                    if key != 'pauli_decomposition':
                        writer.writerow(['Hamiltonian', key, value])
                
                # Write Pauli terms
                if 'pauli_decomposition' in hamiltonian:
                    writer.writerow([])  # Empty row
                    writer.writerow(['Pauli Operator', 'Coefficient', ''])
                    for term in hamiltonian['pauli_decomposition']:
                        writer.writerow([term['operator'], term['coefficient'], ''])
            
            # Write simulation info
            if 'simulation' in data:
                simulation = data['simulation']
                for key, value in simulation.items():
                    if key not in ['energy_evolution', 'final_amplitudes']:
                        writer.writerow(['Simulation', key, value])
                
                # Write energy evolution
                if 'energy_evolution' in simulation:
                    writer.writerow([])  # Empty row
                    writer.writerow(['Time', 'Total Energy', 'Kinetic Energy', 'Potential Energy'])
                    for point in simulation['energy_evolution']:
                        writer.writerow([
                            point['time'],
                            point['total_energy'],
                            point['kinetic_energy'],
                            point['potential_energy']
                        ])
    
    def _extract_qasm_from_data(self, data):
        """Extract QASM circuit from data"""
        if 'simulation' in data and 'circuit_qasm' in data['simulation']:
            return data['simulation']['circuit_qasm']
        else:
            return "// No QASM circuit available"
    
    def _format_bytes(self, bytes):
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} PB"