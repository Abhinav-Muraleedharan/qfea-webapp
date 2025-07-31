# Q_FEA Web Application

A comprehensive web application for **Quantum Finite Element Analysis**, bridging classical structural mechanics with quantum computing simulations.

![Q_FEA Banner](https://img.shields.io/badge/Q_FEA-Quantum%20FEA-blue?style=for-the-badge&logo=quantum)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=flat-square&logo=flask)
![Qiskit](https://img.shields.io/badge/Qiskit-0.43+-purple?style=flat-square&logo=qiskit)

## 🚀 Features

### Core Capabilities
- **📁 Mesh Upload & Processing**: Support for `.vtk`, `.mesh`, `.msh`, `.obj`, `.stl`, `.ply` formats
- **🔬 Finite Element Analysis**: Automated computation of stiffness and mass matrices
- **⚛️ Quantum Hamiltonian Generation**: Convert classical matrices to quantum operators
- **🎯 Quantum Simulation**: Time evolution using Trotter decomposition
- **📊 Advanced Visualization**: 3D mesh rendering, matrix plots, energy evolution
- **💾 Export Capabilities**: JSON, CSV, and QASM circuit export

### Web Interface
- **🎨 Modern UI**: Glassmorphism design with responsive layout
- **📱 Mobile Friendly**: Works seamlessly on desktop and mobile devices
- **⚡ Real-time Updates**: WebSocket integration for live progress tracking
- **🔄 Interactive Visualizations**: 3D mesh viewer with Three.js and plots with Plotly

### Advanced Features
- **🏗️ Material Presets**: Pre-configured materials (steel, aluminum, concrete, etc.)
- **🔧 Parameter Tuning**: Real-time material property adjustments
- **📈 Energy Analysis**: Kinetic and potential energy evolution tracking
- **🌊 Quantum State Visualization**: Amplitude and probability distributions
- **🔍 Circuit Analysis**: Gate count, depth, and complexity metrics

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB (16GB recommended for larger simulations)
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows

### Dependencies
```bash
# Core web framework
Flask>=2.3.0
Flask-CORS>=4.0.0

# Scientific computing
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0

# Quantum computing
qiskit>=0.43.0

# Finite element analysis
sfepy>=2023.2

# Performance optimization
jax>=0.4.0 (optional, for GPU acceleration)
```

## 🛠️ Installation

### Option 1: Quick Start (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-username/qfea-webapp.git
cd qfea-webapp

# Run setup script
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh

# Start the application
python run.py
```

### Option 2: Manual Installation
```bash
# Clone and navigate
git clone https://github.com/your-username/qfea-webapp.git
cd qfea-webapp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Start the application
python run.py
```

### Option 3: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

## 🏃‍♂️ Quick Start Guide

### 1. Upload a Mesh
```bash
# Start the application
python run.py

# Open browser to http://localhost:5000
# Drag and drop a mesh file or click to browse
```

### 2. Configure Materials
```python
# Example material properties
{
    "young_modulus": 200e9,    # Pa (Steel)
    "poisson_ratio": 0.3,      # Dimensionless
    "density": 7850            # kg/m³
}
```

### 3. Run Simulation
```bash
# Set simulation parameters
- Time: 1.0 seconds
- Trotter Steps: 10
- Max Pauli Terms: 100

# Click "Run Quantum Simulation"
```

### 4. Analyze Results
- **Matrices Tab**: View stiffness/mass matrix properties
- **Hamiltonian Tab**: Explore Pauli decomposition
- **Quantum Tab**: Examine circuit structure and metrics
- **Energy Tab**: Analyze energy evolution over time

## 📚 API Documentation

### Core Endpoints

#### Upload Mesh
```http
POST /api/upload
Content-Type: multipart/form-data

file: <mesh_file>
```

#### Compute Matrices
```http
POST /api/process_matrices
Content-Type: application/json

{
    "file_id": "uuid",
    "material_properties": {
        "young_modulus": 200e9,
        "poisson_ratio": 0.3,
        "density": 7850
    }
}
```

#### Run Quantum Simulation
```http
POST /api/run_simulation
Content-Type: application/json

{
    "file_id": "uuid",
    "simulation_params": {
        "time": 1.0,
        "trotter_steps": 10,
        "max_pauli_terms": 100
    }
}
```

### Response Format
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        // Result data here
    }
}
```

## 🏗️ Architecture

### Project Structure
```
Q_FEA_WebApp/
├── 📁 app/                 # Flask application
│   ├── 📄 __init__.py      # App factory
│   ├── 📄 config.py        # Configuration
│   ├── 📁 api/             # REST API routes
│   ├── 📁 services/        # Business logic
│   └── 📁 static/          # Frontend assets
├── 📁 qfea_core/           # Core Q_FEA algorithms
│   ├── 📁 classical_utils/ # FEA computations
│   └── 📁 quantum_utils/   # Quantum simulations
├── 📁 templates/           # HTML templates
├── 📁 tests/               # Test suite
└── 📄 run.py              # Application entry point
```

### Technology Stack
- **Backend**: Flask, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: Three.js, Plotly.js
- **Quantum**: Qiskit, NetworkX
- **Scientific**: NumPy, SciPy, JAX
- **FEA**: SfePy, VTK, MeshIO

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test categories
python -m pytest tests/test_api.py -v
python -m pytest tests/test_mesh_processing.py -v
python -m pytest tests/test_quantum_simulation.py -v
```

### Test Structure
```
tests/
├── test_api.py              # API endpoint tests
├── test_mesh_processing.py  # Mesh processing tests
├── test_quantum_simulation.py # Quantum simulation tests
└── fixtures/               # Test data files
    ├── sample_beam.vtk
    ├── sample_plate.mesh
    └── test_materials.json
```

## 🚀 Deployment

### Production Deployment

#### Option 1: Docker (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With SSL and nginx
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2: Manual Deployment
```bash
# Install production dependencies
pip install -r requirements.txt
pip install gunicorn supervisor

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app

# Or with supervisor for process management
supervisord -c supervisor.conf
```

### Environment Variables
```bash
# .env file
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/qfea_db
MAX_QUBITS=20
USE_GPU=false
```

### Scaling Considerations
- **CPU**: Multi-core systems recommended for parallel matrix computations
- **Memory**: RAM scales exponentially with qubit count (16GB for 20+ qubits)
- **Storage**: Plan for large matrix files and result caching
- **Network**: Consider CDN for static assets in production

## 📊 Performance Benchmarks

### Typical Performance Metrics
| Mesh Size | Vertices | Elements | Matrix Time | Hamiltonian Time | Qubits | Memory |
|-----------|----------|----------|-------------|------------------|--------|---------|
| Small     | 100      | 200      | 2s          | 5s               | 8      | 512MB   |
| Medium    | 1,000    | 2,000    | 15s         | 45s              | 12     | 2GB     |
| Large     | 10,000   | 20,000   | 120s        | 600s             | 16     | 8GB     |
| X-Large   | 100,000  | 200,000  | 1200s       | 3600s            | 20     | 32GB    |

### Optimization Tips
- **GPU Acceleration**: Enable JAX/CuPy for 5-10x speedup
- **Parallel Processing**: Use multi-core systems for matrix computations  
- **Sparse Matrices**: Leverage sparsity for memory efficiency
- **Batch Processing**: Process multiple Pauli terms simultaneously

## 🔧 Configuration

### Material Presets
```python
# Built-in materials
MATERIALS = {
    'steel': {
        'young_modulus': 200e9,
        'poisson_ratio': 0.3,
        'density': 7850
    },
    'aluminum': {
        'young_modulus': 70e9,
        'poisson_ratio': 0.33,
        'density': 2700
    },
    'concrete': {
        'young_modulus': 30e9,
        'poisson_ratio': 0.2,
        'density': 2400
    }
}
```

### Simulation Limits
```python
# Safety limits
MAX_QUBITS = 20                 # Quantum simulation limit
MAX_PAULI_TERMS = 1000         # Hamiltonian decomposition limit
MAX_CONTENT_LENGTH = 500MB      # File upload limit
COMPUTATION_TIMEOUT = 3600      # 1 hour timeout
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Memory Errors
```bash
# Symptoms: Out of memory during matrix computation
# Solution: Reduce mesh size or increase system RAM
# Alternative: Use sparse matrix methods
```

#### 2. Qiskit Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'qiskit'
pip install qiskit>=0.43.0

# For GPU support
pip install qiskit-aer-gpu
```

#### 3. VTK/Mesh Loading Issues
```bash
# Error: Cannot read mesh file
pip install vtk meshio

# For additional format support
pip install meshio[all]
```

#### 4. Performance Issues
```bash
# Enable parallel processing
export OMP_NUM_THREADS=4
export JAX_ENABLE_X64=true

# For GPU acceleration
export CUDA_VISIBLE_DEVICES=0
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

python run.py
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/your-username/qfea-webapp.git
cd qfea-webapp

# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

### Code Style
```bash
# Format code
black app/ qfea_core/ tests/

# Lint code
flake8 app/ qfea_core/ tests/

# Type checking
mypy app/ --ignore-missing-imports
```

### Contribution Guidelines
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SfePy Project** for finite element analysis tools
- **Qiskit Team** for quantum computing framework
- **Flask Community** for the excellent web framework
- **Three.js Contributors** for 3D visualization capabilities

## 📞 Support

### Get Help
- **📖 Documentation**: [docs/](docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/your-username/qfea-webapp/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-username/qfea-webapp/discussions)
- **📧 Email**: abhi98m@cs.toronto.edu

### Citation
If you use Q_FEA in your research, please cite:
```bibtex
@software{qfea_webapp,
  title={Q_FEA: Quantum Finite Element Analysis Web Application},
  author={Muraleedharan, Abhinav},
  year={2024},
  url={https://github.com/your-username/qfea-webapp}
}
```

## 🚀 What's Next?

### Roadmap
- [ ] **Multi-physics Support**: Heat transfer, fluid dynamics
- [ ] **Cloud Integration**: AWS, Google Cloud quantum simulators  
- [ ] **Advanced Visualizations**: Mode shapes, stress animations
- [ ] **Machine Learning**: Predictive modeling for quantum advantage
- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Collaborative Features**: Team workspaces and sharing

### Current Version: 1.0.0
- ✅ Core finite element analysis
- ✅ Quantum Hamiltonian generation  
- ✅ Trotter circuit synthesis
- ✅ Web-based visualization
- ✅ Export capabilities
- ✅ Docker deployment

---

**Built with ❤️ for the quantum computing and structural engineering communities**