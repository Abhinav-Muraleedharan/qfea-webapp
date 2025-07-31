#!/bin/bash

# Q_FEA Web Application Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 Setting up Q_FEA Web Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python $REQUIRED_VERSION or higher required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "Virtual environment activated (Windows)"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "Pip upgraded"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install main dependencies
    pip install -r requirements.txt
    
    # Install the package in development mode
    pip install -e .
    
    print_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "logs"
        "temp"
        "temp/metadata"
        "temp/results"
        "temp/exports"
        "app/static/uploads"
        "tests/fixtures"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "Created directory: $dir"
    done
    
    # Create .gitkeep files
    touch app/static/uploads/.gitkeep
    touch tests/fixtures/.gitkeep
    
    print_success "Directories created"
}

# Copy environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from example"
            print_warning "Please review and update .env file with your settings"
        else
            print_warning ".env.example not found, creating basic .env"
            cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
HOST=0.0.0.0
PORT=5000
MAX_QUBITS=20
EOF
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Install optional GPU dependencies
install_gpu_deps() {
    read -p "Install GPU acceleration dependencies? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing GPU dependencies..."
        
        # Check if CUDA is available
        if command -v nvcc &> /dev/null; then
            pip install cupy-cuda12x cuquantum
            print_success "GPU dependencies installed"
        else
            print_warning "CUDA not found. Installing CPU-only JAX"
            pip install jax[cpu]
        fi
    else
        print_status "Skipping GPU dependencies"
    fi
}

# Run tests
run_tests() {
    read -p "Run test suite? (Y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_status "Running test suite..."
        
        if command -v pytest &> /dev/null; then
            python -m pytest tests/ -v --tb=short
            print_success "Tests completed"
        else
            print_warning "pytest not available, skipping tests"
        fi
    fi
}

# Setup development tools
setup_dev_tools() {
    read -p "Install development tools (black, flake8, pre-commit)? (Y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_status "Installing development tools..."
        
        pip install black flake8 pre-commit mypy
        
        # Setup pre-commit hooks if .pre-commit-config.yaml exists
        if [ -f ".pre-commit-config.yaml" ]; then
            pre-commit install
            print_success "Pre-commit hooks installed"
        fi
        
        print_success "Development tools installed"
    fi
}

# Create sample mesh files for testing
create_sample_files() {
    print_status "Creating sample test files..."
    
    # Create a simple sample mesh in VTK format
    cat > tests/fixtures/sample_beam.vtk << 'EOF'
# vtk DataFile Version 3.0
Simple beam mesh
ASCII
DATASET UNSTRUCTURED_GRID

POINTS 8 float
0.0 0.0 0.0
1.0 0.0 0.0
1.0 1.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
1.0 1.0 1.0
0.0 1.0 1.0

CELLS 1 9
8 0 1 2 3 4 5 6 7

CELL_TYPES 1
12
EOF
    
    print_success "Sample files created"
}

# Final instructions
print_instructions() {
    print_success "🎉 Setup completed successfully!"
    echo
    echo "To start the Q_FEA Web Application:"
    echo
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate     # Windows"
    echo
    echo "2. Start the application:"
    echo "   python run.py"
    echo
    echo "3. Open your browser to:"
    echo "   http://localhost:5000"
    echo
    echo "📚 Additional commands:"
    echo "   pytest tests/           # Run tests"
    echo "   black app/ qfea_core/   # Format code"
    echo "   flake8 app/             # Lint code"
    echo
    echo "📖 Check README.md for detailed documentation"
    echo
}

# Main execution
main() {
    echo "=================================================="
    echo "       Q_FEA Web Application Setup"
    echo "=================================================="
    echo
    
    check_python
    create_venv
    activate_venv
    upgrade_pip
    install_dependencies
    create_directories
    setup_env
    install_gpu_deps
    setup_dev_tools
    create_sample_files
    run_tests
    
    echo
    print_instructions
}

# Run main function
main "$@"