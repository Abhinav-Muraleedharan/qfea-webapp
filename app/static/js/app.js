/**
 * Main application JavaScript for Q_FEA Web Interface
 */

let currentFileId = null;

// Material presets
const materialPresets = {
    steel: { young_modulus: 200e9, poisson_ratio: 0.3, density: 7850 },
    aluminum: { young_modulus: 70e9, poisson_ratio: 0.33, density: 2700 },
    concrete: { young_modulus: 30e9, poisson_ratio: 0.2, density: 2400 },
    titanium: { young_modulus: 110e9, poisson_ratio: 0.34, density: 4500 },
    copper: { young_modulus: 110e9, poisson_ratio: 0.35, density: 8960 }
};

// Initialize when document is ready
$(document).ready(function() {
    initializeEventHandlers();
});

function initializeEventHandlers() {
    // Material preset change handler
    $('#materialPreset').on('change', function() {
        const preset = $(this).val();
        if (preset && materialPresets[preset]) {
            const material = materialPresets[preset];
            $('#youngModulus').val(material.young_modulus);
            $('#poissonRatio').val(material.poisson_ratio);
            $('#density').val(material.density);
        }
    });

    // Upload form handler
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        uploadMesh();
    });

    // Run simulation button handler
    $('#runSimulationBtn').on('click', function() {
        runSimulation();
    });

    // Export button handlers
    $('#exportJsonBtn').on('click', function() {
        exportResults('json');
    });

    $('#exportCsvBtn').on('click', function() {
        exportResults('csv');
    });

    $('#exportQasmBtn').on('click', function() {
        exportResults('qasm');
    });
}

function uploadMesh() {
    const formData = new FormData();
    const fileInput = document.getElementById('meshFile');
    const file = fileInput.files[0];

    if (!file) {
        showError('Please select a file');
        return;
    }

    formData.append('file', file);
    formData.append('young_modulus', $('#youngModulus').val());
    formData.append('poisson_ratio', $('#poissonRatio').val());
    formData.append('density', $('#density').val());

    // Disable upload button
    $('#uploadBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Uploading...');

    // Show progress
    showProgress('Uploading mesh file...', 0);

    $.ajax({
        url: '/api/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                currentFileId = response.data.file_id;
                showSuccess('Mesh uploaded successfully!');
                displayMeshInfo(response.data);
                $('#runSimulationBtn').prop('disabled', false);
                hideProgress();
            } else {
                showError(response.message);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON ? xhr.responseJSON.message : 'Upload failed';
            showError(error);
        },
        complete: function() {
            $('#uploadBtn').prop('disabled', false).html('<i class="fas fa-upload"></i> Upload Mesh');
        }
    });
}

function runSimulation() {
    if (!currentFileId) {
        showError('Please upload a mesh first');
        return;
    }

    const params = {
        time: parseFloat($('#simTime').val()),
        trotter_steps: parseInt($('#trotterSteps').val()),
        max_pauli_terms: parseInt($('#maxPauliTerms').val())
    };

    // Disable button
    $('#runSimulationBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Running...');

    // Show progress
    showProgress('Initializing quantum simulation...', 10);

    $.ajax({
        url: `/api/simulate/${currentFileId}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(params),
        success: function(response) {
            if (response.success) {
                showSuccess('Simulation completed successfully!');
                displayResults(response.data);
                hideProgress();
            } else {
                showError(response.message);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON ? xhr.responseJSON.message : 'Simulation failed';
            showError(error);
        },
        complete: function() {
            $('#runSimulationBtn').prop('disabled', false).html('<i class="fas fa-play"></i> Run Simulation');
        }
    });
}

function displayMeshInfo(data) {
    const meshInfo = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>File ID:</strong> ${data.file_id}</p>
                <p><strong>Filename:</strong> ${data.filename}</p>
                <p><strong>Size:</strong> ${data.file_size}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Nodes:</strong> ${data.mesh_info.num_nodes || 'N/A'}</p>
                <p><strong>Elements:</strong> ${data.mesh_info.num_elements || 'N/A'}</p>
                <p><strong>DOFs:</strong> ${data.mesh_info.num_dofs || 'N/A'}</p>
            </div>
        </div>
    `;
    $('#meshInfo').html(meshInfo);
    $('#meshInfoCard').removeClass('d-none');
}

function displayResults(data) {
    let resultsHtml = '<div class="row">';

    // Display eigenvalues
    if (data.eigenvalues) {
        resultsHtml += `
            <div class="col-md-6 mb-3">
                <h6>Eigenvalues (First 5)</h6>
                <ul class="list-group">
                    ${data.eigenvalues.slice(0, 5).map((val, idx) =>
                        `<li class="list-group-item">»${idx + 1}: ${val.toExponential(4)}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    // Display circuit info
    if (data.circuit_info) {
        resultsHtml += `
            <div class="col-md-6 mb-3">
                <h6>Circuit Information</h6>
                <ul class="list-group">
                    <li class="list-group-item">Qubits: ${data.circuit_info.num_qubits || 'N/A'}</li>
                    <li class="list-group-item">Gates: ${data.circuit_info.num_gates || 'N/A'}</li>
                    <li class="list-group-item">Depth: ${data.circuit_info.depth || 'N/A'}</li>
                    <li class="list-group-item">Pauli Terms: ${data.circuit_info.num_pauli_terms || 'N/A'}</li>
                </ul>
            </div>
        `;
    }

    resultsHtml += '</div>';

    // Display computation time
    if (data.computation_time) {
        resultsHtml += `
            <div class="alert alert-info mt-3">
                <strong>Computation Time:</strong> ${data.computation_time.toFixed(2)}s
            </div>
        `;
    }

    $('#resultsContent').html(resultsHtml);
    $('#resultsCard').removeClass('d-none');
}

function exportResults(format) {
    if (!currentFileId) {
        showError('No results to export');
        return;
    }

    window.location.href = `/api/export/${currentFileId}/${format}`;
}

function showProgress(message, percent) {
    $('#progressSection').removeClass('d-none');
    $('#progressBar').css('width', percent + '%').text(percent + '%');
    $('#progressText').text(message);
}

function hideProgress() {
    $('#progressSection').addClass('d-none');
}

function showSuccess(message) {
    $('#statusMessage')
        .removeClass('alert-danger alert-warning alert-secondary')
        .addClass('alert-success')
        .html(`<i class="fas fa-check-circle"></i> ${message}`);
}

function showError(message) {
    $('#statusMessage')
        .removeClass('alert-success alert-warning alert-secondary')
        .addClass('alert-danger')
        .html(`<i class="fas fa-exclamation-circle"></i> ${message}`);
    hideProgress();
}

function showInfo(message) {
    $('#statusMessage')
        .removeClass('alert-danger alert-success alert-secondary')
        .addClass('alert-warning')
        .html(`<i class="fas fa-info-circle"></i> ${message}`);
}
