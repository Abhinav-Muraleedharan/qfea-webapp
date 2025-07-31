#!/bin/bash

# Set root directory
ROOT="Q_FEA_WebApp"

# Create main folder
mkdir -p $ROOT

# Create root-level files
touch $ROOT/{README.md,requirements.txt,setup.py,Dockerfile,docker-compose.yml,.env.example,.gitignore,run.py}

# Create app folder and subfolders
mkdir -p $ROOT/app/{models,api,services,static/{css,js,uploads}}
touch $ROOT/app/__init__.py
touch $ROOT/app/config.py
touch $ROOT/app/models/{__init__.py,mesh.py}
touch $ROOT/app/api/{__init__.py,routes.py,utils.py}
touch $ROOT/app/services/{__init__.py,mesh_processor.py,quantum_simulator.py,file_handler.py}
touch $ROOT/app/static/css/styles.css
touch $ROOT/app/static/js/{app.js,visualization.js,quantum.js}
touch $ROOT/app/static/uploads/.gitkeep

# Create templates folder and files
mkdir -p $ROOT/templates
touch $ROOT/templates/{index.html,base.html}

# Create qfea_core and submodules
mkdir -p $ROOT/qfea_core/{classical_utils,quantum_utils}
touch $ROOT/qfea_core/__init__.py
touch $ROOT/qfea_core/classical_utils/{__init__.py,generate_mesh.py,compute_pauli_coeffs.py,compute_pauli_coeffs_batch_parallel.py,compute_pauli_coeffs_parallel.py,hamiltonian_prep.py,hamiltonian_prep_sparse.py}
touch $ROOT/qfea_core/quantum_utils/{__init__.py,tensor_network_simulator.py,trotter_circuit_synthesis.py}

# Create tests folder and files
mkdir -p $ROOT/tests
touch $ROOT/tests/{__init__.py,test_api.py,test_mesh_processing.py,test_quantum_simulation.py}

# Create scripts folder and files
mkdir -p $ROOT/scripts
touch $ROOT/scripts/{setup_environment.sh,run_tests.sh}

# Create docs folder and files
mkdir -p $ROOT/docs
touch $ROOT/docs/{api_documentation.md,installation.md,usage_guide.md}

echo "Folder structure for $ROOT created successfully."
