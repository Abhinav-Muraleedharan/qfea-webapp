#!/bin/bash

# Create root-level files
touch README.md requirements.txt setup.py Dockerfile docker-compose.yml .env.example .gitignore run.py

# Create app folder and subfolders
mkdir -p app/models app/api app/services app/static/css app/static/js app/static/uploads
touch app/__init__.py
touch app/config.py
touch app/models/__init__.py app/models/mesh.py
touch app/api/__init__.py app/api/routes.py app/api/utils.py
touch app/services/__init__.py app/services/mesh_processor.py app/services/quantum_simulator.py app/services/file_handler.py
touch app/static/css/styles.css
touch app/static/js/app.js app/static/js/visualization.js app/static/js/quantum.js
touch app/static/uploads/.gitkeep

# Create templates folder and files
mkdir -p templates
touch templates/index.html templates/base.html

# Create qfea_core and submodules
mkdir -p qfea_core/classical_utils qfea_core/quantum_utils
touch qfea_core/__init__.py
touch qfea_core/classical_utils/__init__.py
touch qfea_core/classical_utils/generate_mesh.py
touch qfea_core/classical_utils/compute_pauli_coeffs.py
touch qfea_core/classical_utils/compute_pauli_coeffs_batch_parallel.py
touch qfea_core/classical_utils/compute_pauli_coeffs_parallel.py
touch qfea_core/classical_utils/hamiltonian_prep.py
touch qfea_core/classical_utils/hamiltonian_prep_sparse.py
touch qfea_core/quantum_utils/__init__.py
touch qfea_core/quantum_utils/tensor_network_simulator.py
touch qfea_core/quantum_utils/trotter_circuit_synthesis.py

# Create tests folder and files
mkdir -p tests
touch tests/__init__.py tests/test_api.py tests/test_mesh_processing.py tests/test_quantum_simulation.py

# Create scripts folder and files
mkdir -p scripts
touch scripts/setup_environment.sh scripts/run_tests.sh

# Create docs folder and files
mkdir -p docs
touch docs/api_documentation.md docs/installation.md docs/usage_guide.md

echo "Project substructure created inside $(pwd)"
